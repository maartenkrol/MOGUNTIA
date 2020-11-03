import h5py
#from mpl_toolkits.basemap import Basemap # Import the map plotting interface.
import cartopy#.crs as ccrs
import numpy as np 
import matplotlib.pyplot as plt  # Matplotlib is a scientific plotting package.
from matplotlib.pyplot import cm
from ipywidgets import *
from IPython.display import display
#from IPython.html.widgets import *


class Cwind:
    def __init__(self):
        x           = h5py.File('./DATA/wind.h5','r')
        print(list(x.keys()))
#  =    self.rho    = x['.']['rho'].value
#       self.u      = x['.']['u'].value
#       self.v      = x['.']['v'].value
#       self.w      = x['.']['w'].value
        self.rho    = x['rho'][()]
        self.u      = x['u']  [()]
        self.v      = x['v']  [()]
        self.w      = x['w']  [()]
        x.close()
        self.npn    = 10
        self.latn   = 18
        self.lonn   = 36
        self.month  = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        self.lats   = 85.0 - np.arange(18)*10
        self.lons   = -175 + np.arange(36)*10
        self.action = ToggleButtons(description='Plottype',options=['zonal-aver','lon-pres','lat-pres','lat-lon'],value='zonal-aver')
        self.m_slider    = IntSlider(description='Month',min=1, max=12, step=1, value=0)
        self.lon_slider  = IntSlider(description='Longitude',min=-175, max=175, step=10, value=-175)
        self.lat_slider  = IntSlider(description='Latitude ',min=-85, max=85, step=10, value=5)
        self.pres_slider = IntSlider(description='Pressure ',min=100, max=1000, step=100, value=1000)

        
    def plot_wind(self,action=ToggleButtons(),month=0,lon=0,lat=0,pres=0):
        if action=='zonal-aver':
            self.lat_slider.layout.visibility = "hidden"
            self.lon_slider.layout.visibility = "hidden"
            self.pres_slider.layout.visibility = "hidden"
        elif action == 'lon-pres':
            self.lat_slider.layout.visibility = "visible"
            self.lon_slider.layout.visibility = "hidden"
            self.pres_slider.layout.visibility = "hidden"
        elif action == 'lat-pres':
            self.lat_slider.layout.visibility = "hidden"
            self.lon_slider.layout.visibility = "visible"
            self.pres_slider.layout.visibility = "hidden"
        elif action == 'lat-lon':
            self.lat_slider.layout.visibility = "hidden"
            self.lon_slider.layout.visibility = "hidden"
            self.pres_slider.layout.visibility = "visible"
        else:
            None
            
        imonth = month-1
        itake = int((lon+175)/10)
        jtake = int(17-(lat+85)/10)
        ktake = int(10 - pres/100)
        
        #  get the u wind in the center:
        un = (self.u[imonth,:,:,:]+np.roll(self.u[imonth,:,:,:],1,axis=2))*0.5
        vn = (self.v[imonth,:,0:self.latn,:]+self.v[imonth,:,1:self.latn+1,:])*0.5

        #  get the w-wind at the middle of the pressure layers:
        grav=9.81
        # initially winds are given on: 1000,950,850.....150,100 hPa
        x = [0.0, 0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5, 7.5, 8.5, 9.]
        xinterp = np.arange(10)  # 1000 ---> 100 hPa
        wn=np.zeros((self.npn,self.latn,self.lonn))
        for i in range(self.lonn):
            for j in range(self.latn):
                wn[:,j,i]=np.interp(xinterp,x,self.w[imonth,:,j,i])

        for k in range(self.npn): 
            wn[k,:,:]/=(-self.rho[k]*grav)

        speed = np.sqrt(un**2 + vn**2)

        if action == 'lon-pres':
            wrz = wn[:,jtake,:]
            urz = un[:,jtake,:]
            speedz = speed[:,jtake,:]
            maxx = np.max(np.abs(urz))
            maxy = np.max(np.abs(wrz))

            Y,X = np.mgrid[ 1000:100:10j, -175:175:36j]
            yv = wrz/maxy
            xv = urz/maxx
            plot1,ax = plt.subplots(figsize=(10,6))
            plt.quiver(X, Y, xv, yv,        # data
                       speedz,                   # colour the arrows based on this array
                       cmap=cm.rainbow,     # colour map
                       headlength=7)        # length of the arrows
            ax.set_xlim(-180,180)
            ax.set_ylim(1050,50)
            ax.set_xlabel('Longitude (deg E)')
            ax.set_ylabel('Pressure (hPa)')
            if self.lats[jtake]> 0.:
                ax.text(-170,150,'Latitude: %4iN'%(int(self.lats[jtake])))
            else:
                ax.text(-170,150,'Latitude: %4iS'%(-int(self.lats[jtake])))
            ax.text(50,150,'Month: %s'%(self.month[imonth]))
            ax.text(50,970,'Max w %6.3f m/s'%(maxy))
            ax.text(-170,970,'Max u %6.0f m/s'%(maxx))





            plt.title('Windfield (color: horizontal windspeed (m/s))')
            plt.colorbar()
            plt.show(plot1)                 # display the plot

        elif action == 'lat-pres':
            wrz = wn[:,:,itake]
            vrz = vn[:,:,itake]
            speedz = speed[:,:,itake]
            maxx = np.max(np.abs(vrz))
            maxy = np.max(np.abs(wrz))

            Y,X = np.mgrid[ 1000:100:10j, 85:-85:18j]
            yv = wrz/maxy
            xv = vrz/maxx
            plot1,ax = plt.subplots(figsize=(10,6))
            plt.quiver(X, Y, xv, yv,        # data
                       speedz,                   # colour the arrows based on this array
                       cmap=cm.rainbow,     # colour map
                       headlength=5)        # length of the arrows
            ax.set_xlim(-90,90)
            ax.set_ylim(1050,50)
            ax.set_xlabel('Latitude (deg N)')
            ax.set_ylabel('Pressure (hPa)')
            if self.lons[itake]> 0.:
                ax.text(-85,150,'Longtude: %4iE'%(int(self.lons[itake])))
            else:
                ax.text(-85,150,'Longitude: %4iW'%(-int(self.lons[itake])))
            ax.text(30,150,'Month: %s'%(self.month[imonth]))
            ax.text(30,970,'Max w %6.3f m/s'%(maxy))
            ax.text(-85,970,'Max v %6.1f m/s'%(maxx))




            plt.title('Windfield (color: horizontal windspeed (m/s))')
            plt.colorbar()
            plt.show(plot1)                 # display the plot
        elif action=='zonal-aver':

            # zonal average
            wrz = wn[:,:,:].mean(axis=2)
            vrz = vn[:,:,:].mean(axis=2)
            speedz = speed[:,:,:].mean(axis=2)
            maxx = np.max(np.abs(vrz))
            maxy = np.max(np.abs(wrz))

            y,x = np.mgrid[ 1000:100:10j, 85:-85:18j]
            yv = wrz/maxy
            xv = vrz/maxx
            plot1,ax = plt.subplots(figsize=(10,6))
            plt.quiver(x, y, xv, yv,        # data
                       speedz,              # colour the arrows based on this array
                       cmap=cm.rainbow,     # colour map
                       headlength=5)        # length of the arrows
            #plt.streamplot(x, y, xv, yv,          # data
            #               color=speedz,         # array that determines the colour
            #               cmap=cm.rainbow,        # colour map
            #               linewidth=2,         # line thickness
            #               arrowstyle='->',     # arrow style
            #               arrowsize=1.5)       # arrow size

            ax.set_xlim(-90,90)
            ax.set_ylim(1050,50)
            ax.set_xlabel('latitude (deg N)')
            ax.set_ylabel('pressure (hPa)')
            ax.text(-85,150,'zonal average')
            ax.text(30,150,'month: %s'%(self.month[imonth]))
            ax.text(30,970,'max w %6.3f m/s'%(maxy))
            ax.text(-85,970,'max v %6.1f m/s'%(maxx))

            plt.title('windfield (color: horizontal windspeed (m/s))')
            plt.colorbar()
            plt.show(plot1)                 # display the plot
        elif action=='lat-lon':

            # zonal average
            urz = un[ktake,:,:]
            vrz = vn[ktake,:,:]
            speedz = speed[ktake,:,:]
            maxx = np.max(np.abs(urz))
            maxy = np.max(np.abs(vrz))

            y,x = np.mgrid[ 85:-85:18j,-175:175:36j]
            xv = urz/maxx
            yv = vrz/maxy
            
# --- Basemap            
#           plot1,ax = plt.subplots(figsize=(14,6))
#           m = Basemap(projection='cyl',llcrnrlat=-90,urcrnrlat=90,\
#             llcrnrlon=-180,urcrnrlon=180,resolution='c')
#           m.drawcoastlines()
            #m.fillcontinents(color='coral',lake_color='aqua')
            # draw parallels and meridians.
#           m.drawparallels(np.arange(-90.,91.,30.))
#           m.drawmeridians(np.arange(-180.,181.,60.))
            #m.drawmapboundary(fill_color='aqua')

#           m.quiver(x, y, xv, yv,        # data
#                       speedz,              # colour the arrows based on this array
#                       cmap=cm.rainbow,     # colour map
#                       headlength=5)        # length of the arrows
            #plt.streamplot(x, y, xv, yv,          # data
            #               color=speedz,         # array that determines the colour
            #               cmap=cm.rainbow,        # colour map
            #               linewidth=2,         # line thickness
            #               arrowstyle='->',     # arrow style
            #               arrowsize=1.5)       # arrow size

# --- Cartopy
            import matplotlib.ticker as mticker
            from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
 
            fig1 = plt.figure(1,figsize=(14,6))
            ax = fig1.add_subplot(111, projection=cartopy.crs.PlateCarree(),facecolor='w')
            h=ax.quiver(x, y, xv, yv,        # data
                       speedz,              # colour the arrows based on this array
                       cmap=cm.rainbow,     # colour map
                       headlength=5)
            ax.set_xlabel('logitude (deg E)')
            ax.set_ylabel('latitude (deg N)')
            ax.text(-170,85,'Pressure: %4i hPa'%(1000-ktake*100))
            ax.text(50,85,'month: %s'%(self.month[imonth]))
            ax.text(-170,-85,'max u %6.1f m/s'%(maxx))
            ax.text(50,-85,'max v %6.1f m/s'%(maxy))
            
            ax.add_feature(cartopy.feature.COASTLINE)
            #draw_labels=True ) 
            ax.gridlines(crs=cartopy.crs.PlateCarree(), linewidth=1, color='black', draw_labels=True, alpha=0.5, linestyle='--')
            ax.xlabels_top  = False
            ax.ylabels_left = False
            ax.ylabels_right=True
            ax.xlines       = True
            ax.xlocator     = mticker.FixedLocator([-160, -140, -120, 120, 140, 160, 180,])
            ax.xformatter   = LONGITUDE_FORMATTER
            ax.yformatter   = LATITUDE_FORMATTER
            ax.xlabel_style = {'size': 15, 'color': 'gray'}
            ax.xlabel_style = {'color': 'red', 'weight': 'bold'}
            
            t = ax.set_title('windfield %4i hPa ; month: %s    (color: horizontal windspeed (m/s))'%(1000-ktake*100, self.month[imonth]))
            t.set_position((0.5,1.07))
            plt.colorbar(h)
            plt.show(fig1)                 # display the plot
        else:
            None
       

