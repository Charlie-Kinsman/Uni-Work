from cmath import pi, sqrt, tan
import os
from turtle import shape
import numpy as np
import csv
import random as rand
import math
import matplotlib.pyplot as plt

#Import and format the lifetime data
os.chdir('C:/Users/me/Documents/Uni/Fourth Year/Research Project/Code Stuff')
n_n = np.delete(np.delete(np.genfromtxt('n_n_py.csv', delimiter=','),0,0),0,1)
b_n = np.delete(np.delete(np.genfromtxt('b_n_py.csv', delimiter=','),0,0),0,1)

#Select lifetime columns
n_n_lifetime = n_n[:,2]*3.154e+7
b_n_lifetime = b_n[:,2]*3.154e+7

#Save useful constants
c = 299792458
H_zero = 70*3.24078e-20
om_lam = 0.6889
om_M = 0.315
om_k = 0.0007
aou = 4.15e+17
sec_per_yr = 31536000
no_iter = 100
no_bin_start = 100
scale_factor = 0.001
theta = 0.0872665
k = -10
inter_lum = 0.01

#Set up environment
#Create arrays for time, redshift, star formation rate, binaries born
tim = np.zeros(shape=(no_iter,1))
z = np.zeros(shape=(no_iter,1))
f = np.zeros(shape=(no_iter,1))
F = np.zeros(shape=(no_iter,1))
D_c = np.zeros(shape=(no_iter,1))
sfr = np.zeros(shape=(no_iter,1))
x = np.arange(48,52+inter_lum,inter_lum,dtype=float)
bin_born = np.zeros(shape=(no_iter,1))
bin_born[0] = no_bin_start
#Fill each array with the appropriate formula (Time, Redshift, Star Formation Rate and Coordinate Distance)
for i in range(len(tim)):
    #Time has a fraction of the age of the universe added to it
    tim[i] = tim[i-1] + (aou/no_iter)
    #Time must be converted to redshift (THIS IS FOR A FLAT UNIVERSE)
    z[i] = 1-(math.sqrt(om_M/om_lam)*math.sinh((3*H_zero*math.sqrt(om_lam)*tim[i])/2))**(-2/3)
    #Invert redshift because at the minute it is negative because we are looking into the past
    z[i] = -z[i]
z = np.flip(z,0)
for i in range(len(tim)-1):
    #Use this redshift for the star formation rate formula
    sfr[i] = 0.01*(((1+(z[i]))**2.6)/(1+((1+z[i])/3.2)**6.2))
    #Use numerical integration to calculate coordinate distance
    #Take function inside the intgration
    f[i] = (1/sqrt(((1+(abs(z[i]**2)))*(1+(om_M*abs(z[i]))))-(abs(z[i])*(2+abs(z[i]))*om_lam))).real
    #Use function for manual integration
    F[i] = (F[i-1]+((abs(f[i+1])+(abs(abs(f[i+1])-abs(f[i])))/2)*(z[i+1]-z[i])))
#Put the 0 at the end of F, to the start of the array
F = F[F>0]
F = np.append(0,F)
#Use manual integration results for final distance calculation
D_c = (c/H_zero)*(1/math.sqrt(om_k))*np.sin(math.sqrt(om_k)*F)
D_c_1 = D_c[D_c>0]
D_c_1 = np.append(D_c_1,((2*D_c[len(D_c_1)]) - D_c[len(D_c_1)-1]))
d_D_c = D_c_1 - D_c
m_z = max(z)
z_2 = z[z<max(z)]
z_2 = np.append(z_2,m_z)
z_1 = z[z<max(z)]
z_1 = np.append(0,z_1)
d_z = z_2 - z_1
#Perpendicular scale factor
diff_D_c = d_D_c/d_z
arr = np.zeros(shape=(no_iter,1))
for i in range(len(d_D_c)):
    arr[i] = diff_D_c[i]
diff_D_c = arr
diff_D_c[0] = (2*diff_D_c[1])-diff_D_c[2]
#Area scale factor
ar = (pi*diff_D_c)**2
sw_ar = 1.4*(D_c_1**2)
arr = np.zeros(shape=(no_iter,1))
for i in range(len(d_D_c)):
    arr[i] = sw_ar[i]
sw_ar = arr
sf = sw_ar/ar
sf = np.flip(sf,0)
#Time Dilation Stuff
tim_dil_sf = 1/(1+z)
tim_dil_sf = np.flip(tim_dil_sf,0)
#Luminosity power law
y = x**k
a = np.zeros(shape=(len(y),1))
a_c = np.zeros(shape=(len(y),1))
for i in range(len(y)-1):
    a[i] = inter_lum*(y[i]+((y[i+1]-y[i])/2))
tot_a = np.sum(a)
recip = 1/tot_a
a = np.round(recip*a,6)
for i in range(len(y)-1):
    a_c[i] = a_c[i-1] + a[i]
a_c = np.append(a_c,1)
#Some of the values of the sfr are effectively zero, so we need to discard of them and replace with zero
for i in range(len(sfr)):
    if sfr[i] == math.nan:
        sfr[i] = 0
#Use the star formation rate to inform how many binaries are going to be added at every step
for i in range(len(tim)):
    if i<len(tim)-1:
        bin_born[i+1] = np.round(bin_born[i] + ((sfr[i]*(aou/no_iter))*(1/sec_per_yr)*scale_factor))
    else:
        bin_born[0] = np.round(no_bin_start)
#Make integer as you can't have a fraction of a binary being born
bin_born = bin_born.astype(int)

####################################################################################################
###############################Neutron Star - Neutron Star Simulation###############################
####################################################################################################
#Assign an array to storing the number of neutron stars at each step
num_n_n = np.zeros(shape = (len(tim),1))
num_n_n_grb = np.zeros(shape = (len(tim),1))
#Assign an array to store the neutron stars, starting at no_bin_start
n_n_sim = np.zeros(shape = (1,1))
for i in range(len(tim)):
    print(i)
    #Binary born
    n_n_sim = np.append(n_n_sim,np.zeros(shape=(int(bin_born[i]),1)))
    #Assign Lifetime
    for j in range(len(n_n_sim)):
        if n_n_sim[j] == 0:
            n_n_sim[j] = n_n_lifetime[rand.randint(0,(len(n_n_lifetime)-1))] + tim[i]
    #Remove any that have exceeded their lifetime or luminosities
    n_n_sim_grb = n_n_sim[n_n_sim <= tim[i]]
    n_n_sim = n_n_sim[n_n_sim > tim[i]]
    #Assign Luminosity
    n_n_lum = np.zeros(shape = (len(n_n_sim_grb),1))
    for j in range(len(n_n_sim_grb)):
        if n_n_lum[j] == 0:
            v = 0
            ran = rand.uniform(0,1)
            while v<len(a_c):
                if a_c[v]<=ran<a_c[v+1]:
                    n_n_lum[j] = x[v]
                    n_n_lum[j] = 10**n_n_lum[j]
                    n_n_lum[j] = n_n_lum[j]/(4*pi*((100*D_c_1[i])**2))
                    v = v+1
                else:
                    v = v+1
    n_n_lum = n_n_lum[n_n_lum>=(4e-8)]
    #Count up the number of alive binary at each step
    num_n_n[i] = len(n_n_sim)
    num_n_n_grb[i] = len(n_n_lum)
#Scale due to time dilation (for now create new array)
tim_dil_n_n = num_n_n*tim_dil_sf
tim_dil_n_n_grb = num_n_n_grb*tim_dil_sf
#Scale due to geometry (for now create both new array and final array)
geo_n_n = num_n_n*sf
geo_n_n_grb = num_n_n_grb*sf
#Scale for both geometry and time dilation
tot_n_n = tim_dil_sf*sf*num_n_n
tot_n_n_grb = tim_dil_sf*sf*num_n_n_grb
#Write the number of binaries alive and dead at each time step
z = np.flip(z,0)
n_n_header = ['Time','Number Alive','Number Dead','Redshift','Time Dilation Scale Factor','Geometry Scale Factor','Total Binaries (Alive)','Total GRBs']
n_n_csv = np.concatenate([tim,num_n_n,num_n_n_grb,z,tim_dil_sf,sf,tot_n_n,tot_n_n_grb],axis=1)
with open('n_n_sim_data.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(n_n_header)
    writer.writerows(n_n_csv)
####################################################################################################
####################################################################################################
####################################################################################################

####################################################################################################
################################Neutron Star - Black Hole Simulation################################
####################################################################################################
#Assign an array to storing the number of binaries at each step
num_b_n = np.zeros(shape = (len(tim),1))
num_b_n_grb = np.zeros(shape = (len(tim),1))
#Assign an array to store the binaries, starting at no_bin_start
b_n_sim = np.zeros(shape = (1,1))
for i in range(len(tim)):
    print(i)
    #Binaries born
    b_n_sim = np.append(b_n_sim,np.zeros(shape=(int(bin_born[i]),1)))
    #Assign Lifetimes
    for j in range(len(b_n_sim)):
        if b_n_sim[j] == 0:
            b_n_sim[j] = b_n_lifetime[rand.randint(0,(len(b_n_lifetime)-1))] + tim[i]
    #Remove any that have exceeded their lifetime or luminosities
    b_n_sim_grb = b_n_sim[b_n_sim <= tim[i]]
    b_n_sim = b_n_sim[b_n_sim > tim[i]]
    #Assign Luminosity
    b_n_lum = np.zeros(shape = (len(b_n_sim_grb),1))
    for j in range(len(b_n_sim_grb)):
        if b_n_lum[j] == 0:
            v = 0
            ran = rand.uniform(0,1)
            while v<len(a_c):
                if a_c[v]<=ran<a_c[v+1]:
                    b_n_lum[j] = x[v]
                    b_n_lum[j] = 10**b_n_lum[j]
                    b_n_lum[j] = b_n_lum[j]/(4*pi*((100*D_c_1[i])**2))
                    v = v+1
                else:
                    v = v+1
    b_n_lum = b_n_lum[b_n_lum>=(4e-8)]
    #Count up the number of alive binaries at each step
    num_b_n[i] = len(b_n_sim)
    num_b_n_grb[i] = len(b_n_sim_grb)
#Scale due to time dilation (for now create new array)
tim_dil_b_n = num_b_n*tim_dil_sf
tim_dil_b_n_grb = num_b_n_grb*tim_dil_sf
#Scale due to geometry (for now create both new array and final array)
geo_b_n = sf*num_b_n
geo_b_n_grb = num_b_n_grb*sf
#Scale for both geometry and time dilation
tot_b_n = tim_dil_sf*sf*num_b_n
tot_b_n_grb = tim_dil_sf*sf*num_b_n_grb
#Write the number of binaries alive and dead at each time step
b_n_header = ['Time','Number Alive','Number Dead','Redshift','Time Dilation Scale Factor','Geometry Scale Factor','Total Binaries (Alive)','Total GRBs']
b_n_csv = np.concatenate([tim,num_b_n,num_b_n_grb,z,tim_dil_sf,sf,tot_b_n,tot_b_n_grb],axis=1)
with open('b_n_sim_data.csv', 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(b_n_header)
    writer.writerows(b_n_csv)
####################################################################################################
####################################################################################################
####################################################################################################
