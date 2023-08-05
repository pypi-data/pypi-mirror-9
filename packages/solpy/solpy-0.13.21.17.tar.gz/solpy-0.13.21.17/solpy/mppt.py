import modules

PANEL = modules.Module('Mage Solar : USA Powertec Plus 245-6 MNBS')

S = 1000
t = 25
print 'simple', PANEL.output(S,t, simple=True)

v,i = PANEL.mppt_max(S, t)
print 'max', v, i, v*i
