from pylab import *
import glob,os,sys
from datetime import *
try:
    from ipywidgets import *
except:
    from IPython.html.widgets import *
import subprocess
from IPython.display import display,clear_output
from mpl_toolkits.basemap import Basemap
matplotlib.rcParams.update({'font.size': 12})
class plot_moguntia_new:

    def __init__(self):
        self.automatic = True
        self.nlev = 10
        self.conv = 1.0
        self.grid = True
        self.overplot = False
        self.xmax = 1e10
        self.xmin = 0.0
        self.tmin = datetime(1900,1,1,0,0,0)
        self.tmax = datetime(2020,1,1,0,0,0)
        self.stations = False
        self.infiles = glob.glob('*.in')
        self.infiles.sort()
        self.name = 'DUMMY'
        self.molmass = '28.5'
#        interact_manual(self.Moguntia,inputfile = self.infiles)

# to support python2.7 widgets, set up two types of windows:
# 1. windows that allow selection of multiple files (SelectMultiple)
#    select output file, select overplot file, select station
# 2. widgets that can be passed through the interact call.
#     grid (T/F), overplot (T/F), coneversion (ToggleButto
#
#        if len(self.outputfiles) == 0:
#            print("==============================================================")
#            print("No outputfiles generated, bailing out")
#            print("Please add STATION and/or OUTPUT statements in your input file")
#            print("==============================================================")
#            sys.exit(1)
        options = []
        for ii,filen in enumerate(self.infiles):
            options.append(filen)
        self.Input = Dropdown(description="Inputfile",options=options)  
        self.moguntia = ToggleButton(description="Run Model",value=False)


        self.outputfiles = ['xxx']
        options = []
        for ii,filen in enumerate(self.outputfiles):
            filen = filen[:-1]
            options.append(filen)
        self.wof = SelectMultiple(description="Output",options=options)
        self.wof.width=200
        self.wof.value=(options[0],)
        self.wdoit = ToggleButton(description="Make Plots",value=False)
# if stations files is present, read station info:
        for ioutput in options:
            if (ioutput.endswith('stations')):
                self.stations = True
                ofile = open(os.path.join('OUTPUT',ioutput),'r')
                lines = ofile.readlines()
                ofile.close()
                self.nstat = int(lines[0].split()[0])
                self.navg  = int(lines[0].split()[1])
                self.station_names = []
                data = []
                for line in lines[self.nstat+1:]:
                    y = [float(x) for x in line.split()]
                    data.extend(y)
                data = array(data)
                self.xlen = shape(data)[0]
                self.nrec = int(self.xlen/self.nstat)
                self.data = data.reshape((self.nrec,self.nstat))
                for i in range(self.nstat):
                    self.station_names.append(lines[i+1].split()[0])
# only create widget if station output:
                self.wstat = SelectMultiple(description='Stations',options=self.station_names)
                self.wstat.width=200
                self.wstat.value=(self.station_names[0],)
                #display(self.wstat)
# also create the overplot window:

                os.chdir('MEASUREMENTS')
                oplotfiles = glob.glob(self.name.upper()+'_*')
                oplotfiles.sort()
                os.chdir('..')
                self.wo = SelectMultiple(description='Measurement Stations',options=oplotfiles)
                self.wo.width=200
                self.wo.layout.visibility = 'hidden'
                self.woplot=ToggleButton(Description='Overplot',value=False)
                #display(self.wo)

        if not self.stations:
            self.station_names = ['no station']
            self.wstat = SelectMultiple(description='',options=self.station_names)
            self.wstat.width=200
            self.wstat.value=(self.station_names[0],)
            oplotfiles = ['no station']
            self.wo = SelectMultiple(description='',options=oplotfiles)
            self.wo.width=200
            self.wo.layout.visibility = 'hidden'
            self.woplot=ToggleButton(Description='Overplot',value=False)
            
# start the main interaction window:
        wmain = interact(self.plot_file,
                                Input = self.Input,
                                runm = self.moguntia,
                                out=self.wof,stat=self.wstat,op=self.wo, 
                                conversion=ToggleButtons(options=['mol/mol','ppm','ppb','ppt']), 
                                overplot = self.woplot,
                                grid = self.grid,
                                automatic = self.automatic,
                                doit = self.wdoit)
                        

    def Moguntia(self,inputfile = 'test.in'):         
        xfile = open(inputfile,'r')
        outp = subprocess.check_output(['MODEL/MOGUNTIA'],stdin=xfile)
        print(outp.decode("utf-8")) 
        xfile.close()
        xfile = open(inputfile,'r')
        # now process the output:
        lines = xfile.readlines()
        for line in lines:
            if line.startswith('TITLE'): self.title = line.split()[1]
            if line.startswith('START_DATE'): self.start_date = line.split()[1]
            if line.startswith('END_DATE'): self.end_date = line.split()[1]
            if line.startswith('MOLMASS'): self.molmass = line.split()[1]
            if line.startswith('NAME'): self.name = line.split()[1]
        xfile.close()
        xfile = open(os.path.join('OUTPUT',self.title+'files_written'))
        lines = xfile.readlines()
        lines.sort()
        self.outputfiles = lines
 
        #   this is the main routine that will perform the plotting:
    def plot_file(self, 
                  Input = Dropdown(),
                  runm = ToggleButton,
                  out = SelectMultiple(),
                  stat = SelectMultiple(),
                  op = SelectMultiple(),
                  conversion=ToggleButtons(),
                  overplot = ToggleButton(),
                  grid = True,
                  automatic = True,
                  doit = ToggleButton):
                
        # Check if you want to run the model:
        if runm:
            self.Moguntia(self.Input.value)
            self.moguntia.value = False
            # load the results in the widgets:
            options = []
            for ii,filen in enumerate(self.outputfiles):
                filen = filen[:-1]
                options.append(filen)
                self.wof.options = options
            for ioutput in options:
                if (ioutput.endswith('stations')):
                    self.wof.value = (ioutput,)
                    self.stations = True
                    ofile = open(os.path.join('OUTPUT',ioutput),'r')
                    lines = ofile.readlines()
                    ofile.close()
                    self.nstat = int(lines[0].split()[0])
                    self.navg  = int(lines[0].split()[1])
                    self.station_names = []
                    data = []
                    for line in lines[self.nstat+1:]:
                        y = [float(x) for x in line.split()]
                        data.extend(y)
                    data = array(data)
                    self.xlen = shape(data)[0]
                    self.nrec = int(self.xlen/self.nstat)
                    self.data = data.reshape((self.nrec,self.nstat))
                    for i in range(self.nstat):
                        self.station_names.append(lines[i+1].split()[0])
# only create widget if station output:
                    self.wstat.options = self.station_names
                    self.wstat.value = (self.station_names[0],)
# also create the overplot window:

                    os.chdir('MEASUREMENTS')
                    oplotfiles = glob.glob(self.name.upper()+'_*')
                    oplotfiles.sort()
                    os.chdir('..')
                    self.wo.options = oplotfiles



        if overplot:
            self.wo.layout.visibility = 'visible'
        else:
            self.wo.layout.visibility = 'hidden'


        self.grid = grid
        self.conversion=conversion
        if conversion=='mol/mol':
            self.conv = 1.0          
        elif conversion =='ppm':
            self.conv = 1e6
        elif conversion == 'ppb':
            self.conv = 1e9
        elif conversion == 'ppt':
            self.conv = 1e12
        #for ioutput in self.wof.value:
        
        if (not automatic) and (self.automatic):
            self.automatic = False
            self.wlev = IntSlider(min=5,max=30,value=self.nlev,description='nlev')
            self.wmax = BoundedFloatText(value=self.xmax,max=10*self.xmax,min=self.xmin,description="Max")
            self.wmin = BoundedFloatText(value=self.xmin,max=self.xmax,min=0.0,description="Min")
            tmin = self.convert_datetime(self.tmin)
            tmax = self.convert_datetime(self.tmax)
            self.wtmax = BoundedFloatText(value=tmax,max=10*tmax,min=tmin,description="Tmax")
            self.wtmin = BoundedFloatText(value=tmin,max=tmax,min=0.0,description="Tmin")
            
            self.wi = interact(self.get_levels,
                     nlev=self.wlev,
                     Min=self.wmin,
                     Max=self.wmax,
                     Tmin=self.wtmin,
                     Tmax=self.wtmax)
        elif automatic:
            self.automatic = True
            try:
                self.wi.widget.close()
            except:
                None
        else:
            None

            
        station_out = False 
        za_out = False
        ll_out = False
        for ioutput in out:
            if (ioutput.endswith('stations')):
                station_out = True
            elif (ioutput.find('za.') != -1):
                za_out = True
            elif (ioutput.find('ll.') != -1):
                ll_out = True
                # conditional visibility:
        if (not za_out) and (not ll_out): 
            try:
                self.wlev.layout.visibility = 'hidden'
            except:
                None
        else:
            try:
                self.wlev.layout.visibility= 'visible'
            except:
                None
        if station_out: 
            self.wstat.layout.visibility= 'visible'
            self.woplot.layout.visibility= 'visible'
            try:
                self.wtmin.layout.visibility = 'visible'
                self.wtmax.layout.visibility = 'visible'
            except:
                None
        else:
            #self.wstat.layout.visibility= 'hidden'
            self.woplot.layout.visibility= 'hidden'
            self.wo.layout.visibility= 'hidden'
            try:
                self.wtmin.layout.visibility = 'hidden'
                self.wtmax.layout.visibility = 'hidden'
            except:
                None
        if doit:
            for ioutput in out:
                if (ioutput.endswith('stations')):
                    self.plot_station()            
                elif (ioutput.find('za.') != -1):
                    self.plot_za(ioutput)            
                elif (ioutput.find('ll.') != -1):
                    self.plot_ll(ioutput)            
            self.wdoit.value=False
        
    def get_levels(self, nlev = 10, Min = 0.0,Max = 10.0, Tmin=0.0, Tmax=2015.0):
        self.tmin = self.convert_partial_year(Tmin)
        self.tmax = self.convert_partial_year(Tmax)
                     
    def plot_station(self):
        # set up time:
        start_date = [int(self.start_date[0:4]),int(self.start_date[4:6]),int(self.start_date[6:8])]
        xtime = self.navg*(arange(self.nrec)+0.5)/(12.0*360.0)+\
                start_date[0]+(start_date[1]-1)/12.0+(start_date[2]-1)/360.0
        idate = []
        for itime in xtime:
            idate.append(self.convert_partial_year(itime))
        f,ax = subplots()
        f.set_figheight(7)
        f.set_figwidth(10)
        f.autofmt_xdate()
        
        stat = self.wstat.value
        for istat,name in enumerate(self.station_names):
            if name in self.wstat.value:
                ax.plot(idate,self.data[:,istat]*self.conv,label=name)
        if self.wo.layout.visibility == 'visible':
            for ostat in self.wo.value:
                opl = open(os.path.join('MEASUREMENTS',ostat),'r')
                ov = []
                ot = []
                for line in opl.readlines():
                    xx = line.split()
                    year = int(xx[0])
                    mnth = float(xx[1])
                    if mnth >= 13.0:
                        year+=1
                        mnth-=12.
                    imnth=int(mnth)
                    day = 30*(mnth-imnth)
                    if day <= 0: day = 15
                    if day < 1: day = 1
                    day = int(day)
                    ot.append(datetime(year,imnth,day,0,0,0))
                    ov.append(float(xx[2]))
                opl.close()
                ax.plot(ot,ov,'o',label=ostat)            
        
        ax.set_ylabel(self.name + ' ('+self.conversion+')')
        ax.set_xlabel('Time')
        ax.legend(loc="best")
        ax.grid(self.grid)
        if self.automatic:
            self.xmin = ax.get_ylim()[0]
            self.xmax = ax.get_ylim()[1]
            self.tmin = num2date(ax.get_xlim()[0])
            self.tmax = num2date(ax.get_xlim()[1])
        else:
            ax.set_ylim((self.wmin.value,self.wmax.value))
            ax.set_xlim((self.tmin,self.tmax))
        f.show()

    def convert_partial_year(self,number):
        year = int(number)
        d = timedelta(days=(number - year)*365)
        day_one = datetime(year,1,1)
        date = d + day_one
        return date
    
    def convert_datetime(self,date):
        number = date.year + min((date.month*30 + date.day)/365.0,0.999)
        return number
    
    def plot_za(self,ioutput):
        from copy import deepcopy
        self.zaname=ioutput
        if self.automatic:
            self.nlev=10
        else:
            self.nlev=self.wlev.value
        with open(os.path.join('OUTPUT',ioutput),'r') as ofile:
            lines = ofile.readlines()
            self.zafield = zeros((10,18))
            test = array([float(x) for x in lines[0].split()])
            self.zafield = test.reshape((10,18))
            self.zafield*=self.conv
            if self.automatic:
                    self.xmin = self.zafield.min() 
                    self.xmax = self.zafield.max()
        #self.xmin=Min
        #self.xmax=Max
        x = arange(18)*10. - 85.
        y = 1000.0 - arange(10)*100.0
        X,Y = meshgrid(x,y)
        if self.automatic:
            v = self.xmin + arange(self.nlev)*(self.xmax-self.xmin)/(self.nlev-1)
        else:
            v = self.wmin.value + arange(self.nlev)*(self.wmax.value-self.wmin.value)/(self.nlev-1)
        pf = deepcopy(self.zafield)
        pf = pf[:,::-1]
        f,ax = subplots()
        f.set_figheight(7)
        f.set_figwidth(10)
        ax1 = ax.contourf(X,Y,pf,v)
        ax.set_title('Zonally-averaged concentration '+self.zaname)
        ax.set_ylim([1000,100])
        ax.set_ylabel('Pressure (hPa)')
        ax.set_xlabel('Latitude')
        ax.grid(self.grid)
        cbar = colorbar(mappable=ax1,orientation='horizontal')
        cbar.set_label(self.name + ' ('+self.conversion+')')
        
        
    def plot_ll(self,ioutput):
        from copy import deepcopy
        self.llname=ioutput
        if self.automatic:
            self.nlev=10
        else:
            self.nlev=self.wlev.value
            
        x = arange(36)*10. - 175.
        y = arange(18)*10. - 85.
        X,Y = meshgrid(x,y)
        if self.automatic:
            v = self.xmin + arange(self.nlev)*(self.xmax-self.xmin)/(self.nlev-1)
        else:
            v = self.wmin.value + arange(self.nlev)*(self.wmax.value-self.wmin.value)/(self.nlev-1)
        with open(os.path.join('OUTPUT',ioutput),'r') as ofile:
            lines = ofile.readlines()
            nll = int(lines[0])
            self.field = zeros((18,36,nll))
            self.levels = []
            i = 1
            for l in range(nll):
                self.levels.append(int(lines[i]))
                test= array([float(x) for x in lines[i+1].split()])
                self.field[:,:,l] = test.reshape((18,36))
                i+=2

            self.field*=self.conv
            if self.automatic:
                self.xmin = self.field.min() 
                self.xmax = self.field.max()
                v = self.xmin + arange(self.nlev)*(self.xmax-self.xmin)/(self.nlev-1)
            else:
                v = self.wmin.value + arange(self.nlev)*(self.wmax.value-self.wmin.value)/(self.nlev-1)
                
            for il,level in enumerate(self.levels):
                f,ax = subplots()
                f.set_figheight(7)
                f.set_figwidth(10)
                height = '%5i hPa'%(1100-level*100)
                pf = deepcopy(self.field[:,:,il])
                pf = roll(pf,18,axis=1)
                pf = pf[::-1,:]
                xmap = Basemap(projection='cyl',llcrnrlat=-90.,urcrnrlat=90.,llcrnrlon=-180.,urcrnrlon=180.,resolution='c')
                xmap.drawcoastlines(linewidth=0.5,color='0.25')
                ax1 = xmap.contourf(X,Y,pf,v)
                ax.set_title('Concentration at '+height+' '+self.llname)
                cbar = colorbar(mappable=ax1,orientation='horizontal')
                cbar.set_label(self.name + ' ('+self.conversion+')')
       
