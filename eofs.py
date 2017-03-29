# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 14:24:10 2017

@author: Admin
"""

# Importieren der benötigten Pakete
import iris as iris
import matplotlib.pyplot as plt
import iris.coord_categorisation as cat
from scipy import signal
import iris.quickplot as qplt
from eofs.iris import Eof
import numpy as np
# Constraints
###Lambda Funktion fuer Auswahl des Bereichs
#lat_lon_constraint = iris.Constraint(latitude=lambda cell: 35<=cell<=65,
#                                     longitude=lambda cell: 310 <=cell<=360 or 0<=cell<=30)
#temp=iris.load_cube('air.mon.mean.nc')
#print temp.coord('longitude').points
# Einlesen der NetCDF Dateien
sea_level_pressure=iris.load_cube('mslp.mon.mean.nc')
sea_level_pressure = sea_level_pressure.intersection(longitude=(-50, 30))
sea_level_pressure = sea_level_pressure.intersection(latitude=(35, 65))
#print temperature.coord('longitude').points[:]
#temp=temp.intersection(latitude=(35,65),longitude=(30,50))

###add_month fügt eine Dimension mit den Monatsnamen in den Cube hinzu
cat.add_month(sea_level_pressure, 'time', name='month')

###aggregated_by(coords,aggregator), berechnet die monatlichen Mittelwerte
slp_month_mean=sea_level_pressure.aggregated_by('month',iris.analysis.MEAN)

## Vordefinieren der Anomaliematrizen - Cube Beschreibung stimmt dann nicht mehr
slp_anomaly=sea_level_pressure.copy()

## Berechnen der Anomalien
for i in range(len(slp_month_mean[:,0,0].data)): # Schleife von 1 bis 12
    for j in range(i,len(sea_level_pressure[:,0,0].data),12):   # Schleife die von i bis Ende der Daten in 12er Schritten. (Damit immer Jänner-Jänner Mittel Februar,.ect gerechnet wird)
        
        slp_anomaly[j,:,:].data=sea_level_pressure[j,:,:].data-slp_month_mean[i,:,:].data    
                 
## Vordefinieren der Detrend Matrizen - Cube Beschreibung stimmt dann nicht mehr
slp_detrend=sea_level_pressure.copy()
## Berechnen des Trends
slp_detrend.data=signal.detrend(slp_anomaly.data,axis=0)

cube_detr = sea_level_pressure.copy(data = slp_detrend.data)

cat.add_season(cube_detr,'time',name='clim_season')
cat.add_season_year(cube_detr, 'time', name='season_year')
    
cube_anomalies_seasonal = cube_detr.aggregated_by(['clim_season', 'season_year'],iris.analysis.MEAN)
    
constraint_winter = iris.Constraint(clim_season = 'djf')
constraint_spring = iris.Constraint(clim_season = 'mam')
constraint_summer = iris.Constraint(clim_season = 'jja')
constraint_autumn = iris.Constraint(clim_season = 'son')
cube_winter = cube_anomalies_seasonal.extract(constraint_winter)
cube_spring = cube_anomalies_seasonal.extract(constraint_spring)
cube_summer = cube_anomalies_seasonal.extract(constraint_summer)
cube_autumn = cube_anomalies_seasonal.extract(constraint_autumn)

solver = Eof(cube_summer, weights='coslat')
eofs = solver.eofs(neofs=5)
variance_fractions = solver.varianceFraction(neigs=5)

print 'Variance fractions:';print variance_fractions.data
print 'Variance sum:';print (np.sum(variance_fractions.data))

fig=plt.figure(1,figsize=(15,15))
ax=fig.add_subplot(411)
qplt.contourf(eofs[0,:,:],20)
plt.gca().coastlines()
plt.hold(True)
ax2=fig.add_subplot(412)
qplt.contourf(eofs[1,:,:],20)
plt.gca().coastlines()
ax3=fig.add_subplot(413)
qplt.contourf(eofs[2,:,:],20)
plt.gca().coastlines()
ax4=fig.add_subplot(414)
qplt.contourf(eofs[3,:,:],20)
plt.gca().coastlines()
plt.show()

