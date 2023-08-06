# IMPORTS
import numpy as np
import matplotlib as mpl
#mpl.use('TKAgg')
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.gridspec import GridSpec
import os


def plot_simulation(sim_data, H=[], fname=None):
    '''
    This method provides graphics for each system variable, manipulated
    variable and error function and plots the solution of the simulation.
    
    Parameters
    ----------
    
    sim_data : tuple
        Contains collocation points, and simulation results of system and input variables.
    
    H : dict
        Dictionary of the callable error functions
    
    fname : str
        If not None, plot will be saved as <fname>.png
    '''
    
    t, xt, ut = sim_data
    n = xt.shape[1]
    m = ut.shape[1]
    
    z = n + m + len(H.keys())
    z1 = np.floor(np.sqrt(z))
    z2 = np.ceil(z/z1)

    plt.rcParams['figure.subplot.bottom']=.2
    plt.rcParams['figure.subplot.top']= .95
    plt.rcParams['figure.subplot.left']=.13
    plt.rcParams['figure.subplot.right']=.95

    plt.rcParams['font.size']=16

    plt.rcParams['legend.fontsize']=16
    #plt.rc('text', usetex=True)


    plt.rcParams['xtick.labelsize']=16
    plt.rcParams['ytick.labelsize']=16
    plt.rcParams['legend.fontsize']=20

    plt.rcParams['axes.titlesize']=26
    plt.rcParams['axes.labelsize']=26


    plt.rcParams['xtick.major.pad']='8'
    plt.rcParams['ytick.major.pad']='8'

    mm = 1./25.4 #mm to inch
    scale = 3
    fs = [100*mm*scale, 60*mm*scale]

    fff=plt.figure(figsize=fs, dpi=80)


    PP=1
    for i in xrange(n):
        plt.subplot(int(z1),int(z2),PP)
        PP+=1
        plt.plot(t,xt[:,i])
        plt.xlabel(r'$t$')
        plt.title(r'$'+'x%d'%(i+1)+'(t)$')

    for i in xrange(m):
        plt.subplot(int(z1),int(z2),PP)
        PP+=1
        plt.plot(t,ut[:,i])
        plt.xlabel(r'$t$')
        plt.title(r'$'+'u%d'%(i+1)+'(t)$')

    for hh in H:
        plt.subplot(int(z1),int(z2),PP)
        PP+=1
        plt.plot(t,H[hh])
        plt.xlabel(r'$t$')
        plt.title(r'$H_'+str(hh+1)+'(t)$')

    plt.tight_layout()
    
    plt.show()
    
    if fname:
        if not fname.endswith('.png'):
            plt.savefig(fname+'.png')
        else:
            plt.savefig(fname)


class Animation():
    '''
    Provides animation capabilities.
    
    Given a callable function that draws an image of the system state and smiulation data
    this class provides a method to created an animated representation of the system.
    
    
    Parameters
    ----------
    
    drawfnc : callable
        Function that returns an image of the current system state according to :attr:`simdata`
    
    simdata : numpy.ndarray
        Array that contains simulation data (time, system states, input states)
    
    plotsys : list
        List of tuples with indices and labels of system variables that will be plotted along the picture
    
    plotinputs : list
        List of tuples with indices and labels of input variables that will be plotted along the picture
    '''
    
    def __init__(self, drawfnc, simdata, plotsys=[], plotinputs=[]):
        self.fig = plt.figure()
    
        self.image = 0
        
        self.t = simdata[0]
        self.xt = simdata[1]
        self.ut = simdata[2]
        
        self.plotsys = plotsys
        self.plotinputs = plotinputs
        
        self.get_axes()
        
        self.axes['ax_img'].set_frame_on(True)
        self.axes['ax_img'].set_aspect('equal')
        self.axes['ax_img'].set_axis_bgcolor('w')
        
        self.nframes = int(round(24*(self.t[-1] - self.t[0])))
        
        self.draw = drawfnc
        
        # enable LaTeX text rendering --> slow
        #plt.rc('text', usetex=True)
    
    
    class Image():
        '''
        This is just a container for the drawn system.
        '''
        def __init__(self):
            self.patches = []
            self.lines = []
        
        def reset(self):
            self.patches = []
            self.lines = []
    
    
    def get_axes(self):
        sys = self.plotsys
        inputs = self.plotinputs
        
        if not sys+inputs:
            gs = GridSpec(1,1)
        else:
            l = len(sys+inputs)
            
            gs = GridSpec(l, 3)
        
        axes = dict()
        syscurves = []
        inputcurves = []
        
        if not sys+inputs:
            axes['ax_img'] = self.fig.add_subplot(gs[:,:])
        else:
            axes['ax_img'] = self.fig.add_subplot(gs[:,1:])
        
        for i in xrange(len(sys)):
            axes['ax_x%d'%i] = self.fig.add_subplot(gs[i,0])
            
            curve = mpl.lines.Line2D([], [], color='black')
            syscurves.append(curve)
            
            axes['ax_x%d'%i].add_line(curve)
        
        lensys = len(sys)
        for i in xrange(len(inputs)):
            axes['ax_u%d'%i] = self.fig.add_subplot(gs[lensys+i,0])
            
            curve = mpl.lines.Line2D([], [], color='black')
            inputcurves.append(curve)
            
            axes['ax_u%d'%i].add_line(curve)
        
        self.axes = axes
        self.syscurves = syscurves
        self.inputcurves = inputcurves
    
    
    def set_limits(self, ax='ax_img', xlim=(0,1), ylim=(0,1)):
        self.axes[ax].set_xlim(*xlim)
        self.axes[ax].set_ylim(*ylim)
    
    
    def set_label(self, ax='ax_img', label=''):
        self.axes[ax].set_ylabel(label, rotation='horizontal', horizontalalignment='right')
        
    
    def animate(self):
        '''
        Starts the animation of the system.
        '''
        t = self.t
        xt = self.xt
        ut = self.ut
        
        # NEW: try to repeat first and last frame
        pause_time = 1.0 #[s]
        
        # how many frames will be plotted per second of system time
        fps = self.nframes/(t[-1] - t[0])
        
        # add so many frames that they fill the `pause`
        add_frames = int(fps * pause_time)
        
        for i in xrange(add_frames):
            t = np.hstack((t[0],t,t[-1]))
            xt = np.vstack((xt[0],xt,xt[-1]))
            ut = np.vstack((ut[0],ut,ut[-1]))
        
        
        #tt = np.linspace(0,len(t)-1,self.nframes,endpoint=True)
        tt = np.linspace(0,xt.shape[0]-1,self.nframes,endpoint=True)
        tt = np.hstack(([tt[0]]*add_frames,tt,[tt[-1]]*add_frames))
        
        self.T = t[-1] - t[0] + 2 * pause_time
        
        # raise number of frames
        self.nframes += 2 * add_frames
        
        #IPS()
        
        # set axis limits and labels of system curves
        xlim = (0.0, self.T - 2 * pause_time)
        for i, idxlabel in enumerate(self.plotsys):
            idx, label = idxlabel
            
            try:
                ylim = (min(xt[:,idx]), max(xt[:,idx]))
            except:
                ylim = (min(xt), max(xt))
            
            self.set_limits(ax='ax_x%d'%i, xlim=xlim, ylim=ylim)
            self.set_label(ax='ax_x%d'%i, label=label)
            
        # set axis limits and labels of input curves
        for i, idxlabel in enumerate(self.plotinputs):
            idx, label = idxlabel
            
            try:
                ylim = (min(ut[:,idx]), max(ut[:,idx]))
            except:
                ylim = (min(ut), max(ut))
            
            self.set_limits(ax='ax_u%d'%i, xlim=xlim, ylim=ylim)
            self.set_label(ax='ax_u%d'%i, label=label)
        
        def _animate(frame):
            i = tt[frame]
            print "frame = {f}, t = {t}, x = {x}, u = {u}".format(f=frame, t=t[i], x=xt[i,:], u=ut[i,:])
            
            # draw picture
            image = self.image
            ax_img = self.axes['ax_img']
            
            if image == 0:
                # init
                image = self.Image()
            else:
                # update
                for p in image.patches:
                    p.remove()
                for l in image.lines:
                    l.remove()
                image.reset()
            
            image = self.draw(xt[i,:], image=image)
            
            for p in image.patches:
                ax_img.add_patch(p)
            
            for l in image.lines:
                ax_img.add_line(l)
            
            self.image = image
            self.axes['ax_img'] = ax_img
            
            # update system curves
            for k, curve in enumerate(self.syscurves):
                try:
                    curve.set_data(t[:i], xt[:i,self.plotsys[k][0]])
                except:
                    curve.set_data(t[:i], xt[:i])
                self.axes['ax_x%d'%k].add_line(curve)
            
            # update input curves
            for k, curve in enumerate(self.inputcurves):
                try:
                    curve.set_data(t[:i], ut[:i,self.plotinputs[k][0]])
                except:
                    curve.set_data(t[:i], ut[:i])
                self.axes['ax_u%d'%k].add_line(curve)
            
            plt.draw()
        
        self.anim = animation.FuncAnimation(self.fig, _animate, frames=self.nframes, 
                                            interval=1, blit=False)
    
    
    def save(self, fname, fps=None, dpi=200):
        '''
        Saves the animation as a video file or animated gif.
        '''
        if not fps:
            fps = self.nframes/(float(self.T))  # add pause_time here?
        
        if fname.endswith('gif'):
            self.anim.save(fname, writer='imagemagick', fps=fps)
        else:
            FFWriter = animation.FFMpegFileWriter()
            self.anim.save(fname, fps=fps, dpi=dpi, writer='mencoder')
