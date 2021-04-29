import matplotlib.pyplot as plt
import numpy as np
def pv(pv_prev,u):
      out = (pv_prev*1.005)+0.5  
      out = out-(u)
      #out = out + (0.1*np.random.random_sample()) 
      return out
K = 0.05               
Ti = 5             
Td = 0.0002
max_time = 1000
t_steps = 100
setpoint = 253
start_point = 295
step_length = 40
step_height = 10
step_start = 50
t_elements = (max_time*t_steps)+1
tt = np.linspace(start = 0,stop = max_time,num = t_elements)
PV = np.linspace(start = 0,stop = 0,num = t_elements)
U = np.linspace(start = 0,stop = 0,num = t_elements)
E = np.linspace(start = 0,stop = 0,num = t_elements)
EI = np.linspace(start = 0,stop = 0,num = t_elements)
ED = np.linspace(start = 0,stop = 0,num = t_elements)
START_LINE = np.linspace(start = start_point, stop = start_point, num = t_elements)
SP = np.linspace(start = setpoint, stop = setpoint, num = t_elements)
PV[0] = start_point
k=1
while k<(len(tt)):
      PV[k] = pv(PV[k-1],U[k-1])
      E[k] = PV[k]-SP[k]
      EI[k] = EI[k-1]+(E[k]*(1/t_steps))
      ED[k] = (E[k]-E[k-1])*t_steps
      U[k] = K*((E[k])+((1/Ti)*EI[k])+(Td*ED[k]))
      if k == (step_start*t_steps):
            SP[k:(k+(step_length*t_steps))] = PV[k] + step_height
      
      if k == ((step_start*t_steps)+(step_length*t_steps)):
            del_PV = PV[(step_start*t_steps)+(step_length*t_steps)-1] - PV[(step_start*t_steps)]
            del_CV = U[(step_start*t_steps)+(step_length*t_steps)-1] - U[(step_start*t_steps)]
            K_pr = del_PV/(del_CV)
            y_1 = np.linspace(start = 0,stop = 0,num = ((step_length*t_steps)+1))
            y_2 = np.linspace(start = 0,stop = 0,num = ((step_length*t_steps)+1))
            y_3 = np.linspace(start = 0,stop = 0,num = ((step_length*t_steps)+1))
            y_4 = np.linspace(start = 0,stop = 0,num = ((step_length*t_steps)+1))
            y_5 = np.linspace(start = 0,stop = 0,num = ((step_length*t_steps)+1))
            j = 1
            l = 1
            m = 1
            n = 1
            o = 1
            while j<(((step_length*t_steps)+1)):
                  y_1[0] = PV[(step_start*t_steps)]
                  y_1[j] = y_1[j-1] + ((K_pr - (PV[(step_start*t_steps)+j]/step_height))*(1/t_steps))
                  j = j+1
            while l<(((step_length*t_steps)+1)):
                  y_2[0] = y_1[0]
                  y_2[l] = y_2[l-1] + (((y_1[(step_length*t_steps)]) - y_1[l])*(1/t_steps))
                  l = l+1
            while m<(((step_length*t_steps)+1)):
                  y_3[0] = y_2[0]
                  y_3[m] = y_3[m-1] + (((y_2[(step_length*t_steps)]) - y_2[m])*(1/t_steps))
                  m = m+1
            while n<(((step_length*t_steps)+1)):
                  y_4[0] = y_3[0]
                  y_4[n] = y_4[n-1] + (((y_3[(step_length*t_steps)]) - y_3[n])*(1/t_steps))
                  n = n+1
            while o<(((step_length*t_steps)+1)):
                  y_5[0] = y_5[0]
                  y_5[o] = y_5[o-1] + (((y_4[(step_length*t_steps)]) - y_4[o])*(1/t_steps))
                  o = o+1
            A_1 = y_1[(step_length*t_steps)]
            A_2 = y_2[(step_length*t_steps)]
            A_3 = y_3[(step_length*t_steps)]
            A_4 = y_4[(step_length*t_steps)]
            A_5 = y_5[(step_length*t_steps)]
            Td = ((A_3*A_4)-(A_2*A_5))/((A_3*A_3)-(A_1*A_5))
            alpha = ((A_1*A_2)-(Td*A_1*A_1))/(K_pr*A_3)
            Ti = A_1/(K_pr*(1+alpha))
            K = 1/(2*K_pr*alpha)
            print("K")
            print(K)
            print("Ti")
            print(Ti)
            print("Td")
            print(Td)
      k = k+1

print(PV[9000:9050])
plt.subplot(1,2,1)
plt.plot(tt,PV)
plt.plot(tt,START_LINE,color="green")
plt.plot(tt,SP,color="red")
plt.subplot(1,2,2)
plt.plot(tt,U)
plt.show()
