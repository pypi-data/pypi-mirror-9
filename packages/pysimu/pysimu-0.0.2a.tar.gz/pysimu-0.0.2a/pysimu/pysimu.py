# -*- coding: utf-8 -*-
"""

Main pysimu module

Created on Thu Aug 14 20:21:56 2014

@author: jmmauricio-m
"""


import numpy as np
from scipy.integrate import ode
from models.psys import sys_freq_model_1, gen_nc


class sim:
    '''
    
    Class to performe simuations
    
    


    '''    
    

    def __init__(self):
        
        self.x = np.array([])
        self.t = 0.0
        
        self.T = np.array([])
        self.X = np.array([])
        self.Y = np.array([])

        self.max_step = 0.1
        self.nsteps = 5000

        
    def h(self,x):
        
        return x
    
    def odefun(self,t,x):
        self.x = x
        return self.f(t,x)
        
    def odeout(self,t,x):
        
        self.T = np.hstack((self.T,t))
        self.X = np.vstack((self.X,x))
        
        self.Y = np.vstack((self.Y,self.h(t,self.x)))
        
        return self.h(t,self.x)

    def run(self, t_end):
        
        r = ode(self.odefun)
        r.set_integrator('dopri5', max_step=self.max_step,  nsteps = self.nsteps)
        r.set_solout(self.odeout)
        if len(self.X)==0:
            self.X = self.x_0
            self.T = np.array(self.t)
            self.Y = np.array(self.h(self.t,self.x_0))
            
        r.set_initial_value(self.x_0, self.t)
        
        r.integrate(t_end)
        self.t = t_end
        self.r = r
        self.x = r.y

        
        
        
'''
        
>>> r.set_initial_value(y0, t0).set_f_params(2.0).set_jac_params(2.0)
>>> t1 = 10
>>> dt = 1
>>> while r.successful() and r.t < t1:
>>>     r.integrate(r.t+dt)
>>>     print("%g %g" % (r.t, r.y))        
'''     

                
    
    
class system:
    
    def __init__(self):
        
        self.sys_list = []
       
        self.pssys= sys_freq_model_1()
        self.gen_nc = gen_nc()
        
#        n_x_global_ini = 0
#        n_x_global_end = self.pssys.n_x
#        self.pssys.x_idx = range(n_x_global_ini,n_x_global_end)
#        n_x_global_ini = n_x_global_end
#        n_x_global_end = n_x_global_end + self.gen_nc.n_x
#        self.gen_nc.x_idx = range(n_x_global_ini,n_x_global_end)
#        
#        self.dx = np.zeros((3,1))   
        self.max_step = 0.1
        self.nsteps = 5000
        self.x = np.array([]) 
        self.t = 0.0
        self.channels = {}

    def setup(self):

        
        for item_name, item_model in self.models_list:
            exec('self.{:s} = {:s}()'.format(item_name,item_model))
            exec("self.sys_list += [self.{:s}]".format(item_name)) 
         
        k = 0
        for item in self.sys_list:
            item.k = k
            k += item.n_x

        self.chan = {}
        for item_model,item_var in self.channels:
            if not self.chan.has_key(item_model):
                self.chan.update({item_model:{item_var:np.array([])}})
            else:
                self.chan[item_model].update({item_var:np.array([])})

        self.r = ode(self.f)
        self.r.set_integrator('dopri5', max_step =self.max_step, nsteps=self.nsteps)
        self.r.set_solout(self.out)
        self.r.set_initial_value(self.ini(),self.t)
            
    def ini(self):
        
        current_out = ''
        
        for item_out, item_in in self.backward_connections:
            item_name_out, item_var_out = item_out.split('.')
            item_name_in, item_var_in = item_in.split('.')
            if current_out == '':
                exec('self.{:s}.ini()'.format(item_name_out))
                current_out = item_name_out
            to_exec = 'self.{:s}.{:s} = self.{:s}.{:s}'.format(item_name_in,item_var_in,item_name_out,item_var_out)
            print to_exec
            exec(to_exec)
        
        
        x_list = []
        for item in self.sys_list:
            item.ini()
            x_list += [item.x]        
        self.x = np.vstack(x_list)
        return self.x
        
    def f(self,t,x):
        
        self.perturbation(t,x)
        
        
        for item_out, item_in in self.foward_connections:
            item_name_out, item_var_out = item_out.split('.')
            item_name_in, item_var_in = item_in.split('.')
            to_exec = 'self.{:s}.{:s} = self.{:s}.{:s}'.format(item_name_in,item_var_in,item_name_out,item_var_out)
#            print to_exec
            exec(to_exec)
#        print self.pssys.freq
            
            
        dx_list = []
        for item in self.sys_list:
#            print x
            x_i = x[item.k:item.k+item.n_x]
            item.x = x_i
            item.update()
            item.f(t,x_i)
            dx_list += [item.dx]        
        self.dx = np.vstack(dx_list)
 
        return self.dx
       

    def update(self):

        for item in self.sys_list:
            item.update()
        

    def out(self, t,x):
        self.t = t
        for item_model,item_var in self.channels:
            if item_model == 'sys':
                exec('item_value = self.{:s}'.format(item_var))
                self.chan[item_model][item_var] = np.hstack((self.chan[item_model][item_var],item_value))
            else:    
                exec('item_value = self.{:s}.{:s}'.format(item_model,item_var))
                self.chan[item_model][item_var] = np.hstack((self.chan[item_model][item_var],item_value))
#        print self.pssys.freq
    def run(self, t_end):

        self.r.integrate(t_end)
        self.t = t_end
    
    def perturbation(self,t,x):
        pass

       
if __name__ == '__main__':
    
    simu_1 = sim()
    
    p_m = 1.0
    X = 0.5
    e = 1.0
    v = 1.0
    H = 3.5
    omega_s = 1.0
    omega = omega_s
    
    D = 1.0
    
    Omega_b = 2.0*np.pi*50.0
    
    def f(t,x):
        
        delta = x[0]
        omega = x[1]
        
        p_e = e*v/X*np.sin(delta)
        
        ddelta = Omega_b*(omega - omega_s)
        domega = 1.0/(2*H)*(p_m - p_e - D*(omega - omega_s))
        
        return [ddelta, domega]
    
    
    def h(t,x):

        delta = x[0]
        omega = x[1]
        
        p_e = e*v/X*np.sin(delta)
        
        return np.array(p_e)


    p_e = p_m
    delta_0 = np.arcsin(p_e*X/(e*v))  
    omega_0 = omega_s
    x_0 = np.array([delta_0, omega_0])
    
    
    simu_1.f = f
    simu_1.x_0 = x_0
    simu_1.h = h
    simu_1.run(1.0)
    v = 0.0
    simu_1.run(1.2)
    v = 1.0
    simu_1.x_0 = simu_1.x
    simu_1.run(5.0)
    
    
#    sys_1 = system()
#    
#    sys_1.models_list = [('pssys','sys_freq_model_1'),
#                         ('gen_nc','gen_nc')]
#
#    sys_1.backward_connections = [('pssys.p_nc','gen_nc.p_nc')] 
#                           
#    sys_1.foward_connections = [('pssys.freq','gen_nc.freq'),
#                               ('gen_nc.p_nc','pssys.p_nc')]
#                               
#    sys_1.channels = [('sys','t'), 
#                      ('pssys','freq'),
#                      ('pssys','p_nc'), 
#                      ('pssys','p_l')]
#    
#    def perturbation(self,t,x):
#        if t>1.0:
#            self.sys.p_l = 2200.0
#    
#    sys_1.setup()    
##    sys_1.ini()   
#    sys_1.gen_nc.K_f = 100000.0
#    print sys_1.pssys.p_nc  
#    print sys_1.gen_nc.p_nc             
#    sys_1.run(1.0)
#    sys_1.pssys.p_l = 2200.0
#    sys_1.run(10.0)
    
    Delta = np.linspace(0.0, np.pi,100)
    P_e = e*v/X*np.sin(Delta)
#    
    import matplotlib.pyplot as plt
    fig_1 = plt.figure( figsize=(14, 8))
        
    ax_delta = fig_1.add_subplot(2,2,1)
    ax_omega = fig_1.add_subplot(2,2,3)
    ax_delta_omega = fig_1.add_subplot(2,2,(2,4))
    
    ax_delta.plot(simu_1.T,simu_1.X[:,0], linewidth=2)
    ax_omega.plot(simu_1.T,simu_1.X[:,1], linewidth=2)
    ax_delta_omega.plot(Delta,P_e, label='$\sf p_e$')
    ax_delta_omega.plot(Delta,P_e/P_e*p_m, label='$\sf p_m$', linewidth=2)
    ax_delta_omega.plot(simu_1.X[:,0],simu_1.Y[:], 'r', linewidth=2)
    
#    ax_delta.set_xlabel('Time (s)')
    ax_delta.set_ylabel('$\sf \delta $ (rad)')

    ax_omega.set_xlabel('Time (s)')
    ax_omega.set_ylabel('$\sf \omega $ (p.u.)')

    ax_delta_omega.set_xlabel('$\sf \delta $ (rad)')
    ax_delta_omega.set_ylabel('$\sf Power $ (p.u.)')
    
    ax_delta.grid(True)
    ax_omega.grid(True)
    ax_delta_omega.grid(True)
    
    
#    ax_powers = fig_freq.add_subplot(212)
#    ax_powers.plot(sys_1.chan['sys']['t'],sys_1.chan['pssys']['p_nc'])
#    ax_powers.plot(sys_1.chan['t'],sys_1.chan['p_g']) 
    import plotly.plotly as py

    py.sign_in("jmmauricio", "rwdnrmvuyg")
    plot_url = py.plot_mpl(fig_1, auto_open=True)
    
