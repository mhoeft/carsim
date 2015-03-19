import math
import itertools
from scipy.stats import nakagami

class DualSlopeModel():
    def __init__(self):
        self.c = 10.0
        self.c1 = {18:-29.14, 3:-13.64, 4.5:-15.29, 6: -19.85, 9: -22.12, 12: -25.97, 18: -29.14, 24: -39.27, 27:-37.24}
        self.c2 = {18:12.89, 3:8.939, 4.5: 9.228, 6:10.31, 9: 10.93, 12: 12.83, 18: 12.89, 24:18.17, 27:16.17}
        self.c3 = {18:-1.164, 3: -1.3, 4.5: -1.103, 6:-1.313, 9: -1.174, 12: -1.258, 18: -1.164, 24:-1.354, 27:-1.219}
        self.c4 = {18:0.4501, 3: 0.6895, 4.5: 0.5428 , 6: 0.5674, 9: 0.4858, 12: 0.5459, 18: 0.4501, 24:0.5715, 27:0.4811}
        
        self.d1 = {18:0.0001017, 3: 0.0001286, 4.5:0.0001216 , 6:0.0001027, 9: 9.079e-5, 12: 0.0001124, 18: 0.0001017, 24:8.056e-5, 27:8.734e-5 }
        self.d2 = {18:-0.004607, 3:-0.004565, 4.5: -0.004469, 6:-0.004712, 9: -0.003987, 12: -0.006063, 18: -0.004607, 24:-0.0043134, 27:-0.005424}
        self.d3 = {18:8.58e-5, 3:0.0001003, 4.5: 9.348e-5, 6:8.23e-5, 9: 7.308e-5, 12: 8.505e-5, 18: 8.58e-5, 24:6.918e-5, 27:7.552e-5}
        self.d4 = {18:-0.004811, 3:-0.004927, 4.5: -0.004772, 6:-0.00505, 9: -0.004162, 12: -0.006508, 18: -0.004811, 24:-0.004409, 27:-0.005779}
        
        self.l=540.0
        self.lambd = 0.0508
        self.d0 = 10.0
        self.dc = 80.0
        self.Path_gain1 = 1.9 #1.9
        self.Path_gain2 = 3.8



    def SNR(self,Pr,Pn=-99.0):
        return float(Pr-Pn)
        
    def ar(self,l, dr):
        return self.c1[dr]*math.exp(self.d1[dr]*l)+self.c2[dr]*math.exp(self.d2[dr]*l)
    
    def br(self,l, dr):
        return self.c3[dr]*math.exp(self.d3[dr]*l)+self.c4[dr]*math.exp(self.d4[dr]*l)
    
    def PER(self,SINR,l, dr):
        return 0.5*(1.0 - math.tanh(self.ar(l, dr)-self.br(l, dr)*(SINR+self.c)))
    
    def P0(self,d, Pt):
        return Pt + 10.0 * math.log10(self.lambd**2/((4.0*math.pi)**2*d**2))
    
    def Nakagami(self,d):
        m = 3
        if d >= 0 and d <= 50: 
            m = 3.0
        elif d >= 51 and d <= 150: 
            m = 1.5
        elif d > 150: 
            m = 1.0
        return nakagami.rvs(m)        
        #Prl = 10.0**(Pr(d,Pt)/10.0)
        #return float(2.0*m**m*d**(2.0*m-1)*math.exp(((-1)*m*d**2)/Prl)/((Prl**m*math.gamma(m))))
    
    def rcvPower(self,d, Pt=25):
            ####
        # z ETSI TR 102 861
        if d >= self.d0 and d <= self.dc:
            p = self.P0(self.d0, Pt)- 10.0*(self.Path_gain1)*math.log10(d/self.d0)    
        else:
            p = self.P0(self.d0, Pt)- 10.0*(self.Path_gain2)*math.log10(d/self.dc)-10.0*(self.Path_gain1)*math.log10(self.dc/self.d0) 
        n = self.Nakagami(d)
        #print n 
        p_db = 10.0*math.log10(10.0**(p/10)*n)
        return p_db
        #return p
        ####    
        # z A Computationally Inexpensive Empirical Model of IEEE 802.11p Radio Shadowing in Urban Environments
        #return Pt - 10.0*math.log10((16.0*math.pi**2*d**2.2)/lambd**2)
    def dataRate(self,SNR):
        if SNR < 6.0:
            return 3.0
        elif 6.0 <= SNR < 7.0:
            return 4.5
        elif 7.0 <= SNR < 7.5:
            return 6.0
        elif 7.5 <= SNR < 9.5:
            return 9.0
        elif 9.5 <= SNR < 13.0:
            return 12.0
        elif 13.0 <= SNR < 15.0:
            return 18.0
        elif 15.0 <= SNR < 20.0:
            return 24.0
        else:
            return 27.0
        
    def calculateDataRate(self, distance, transPower=25.0):
        Pr = self.rcvPower(distance, transPower)
        snr = self.SNR(Pr)
        return self.dataRate(snr)

    def calculatePER(self, distance, msg_length):
        Pr = self.rcvPower(distance)
        snr = self.SNR(Pr)
        return self.PER(snr, msg_length, 18)

if __name__ == "__main__":
    print "TEST"
    import matplotlib.pyplot as plt
    dsm = DualSlopeModel()
    result_dict1 = {}
    result_dict2 = {}
    resulat_list1 = []
    per_list1 = []
    resulat_list2 = []
    per_list2 = []
    link_rates =  [3,4.5,6,9,12,18,24,27]
    markers = itertools.cycle(['o','s','v', "*", "^", "x", "D", "."]) 
    #link_rates =  [18]
    for lr in link_rates:
            result_dict1[lr] = []
            result_dict2[lr] = []
    for d in xrange(1,1000,10):
        dr1 = dsm.calculateDataRate(d, 25)
        snr1 = dsm.SNR(dsm.rcvPower(d, 25))
        for lr in link_rates:
            tmp_table = []
            for i in range(100):   
                tmp_table.append(dsm.PER(snr1, 512, lr))
            result_dict1[lr].append(sum(tmp_table)/len(tmp_table))
            #result_dict2[lr].append(dsm.PER(snr1, 512, lr))
    for lr in link_rates:
        plt.plot(xrange(1,1000,10), result_dict1[lr], label=str(lr) + "Mbps", marker=markers.next())
        #plt.plot(result_dict2[lr], "r", label=" 1000 B")
    plt.legend(loc=0)
    plt.xlabel("distance [m]", size=20)
    plt.ylabel("Packet Error Rate", size=20)
    plt.show()
