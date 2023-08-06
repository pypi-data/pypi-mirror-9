
.. code:: python

    %matplotlib inline
    import os
    import fluiddyn as fld

Tutorial: working in the laboratory (user perspective)
======================================================

FluidDyn uses the object-oriented programming concepts. It deals with
objects, which is a very natural way to represent and drive experiments
since experiments consist in objects interacting with each other.

Regarding the laboratory, each physical object (a pump, a traverse, a
probe, an acquisition board, a tank filled with a stratified fluid...)
is represented and controlled by an instance of a class. The
experimental results can also be represented by other types of objects.

Example of a conductivity probe attached to a moving traverse
-------------------------------------------------------------

Let's consider a real-life example, how to use a conductivity probe attached to a moving traverse. FluidDyn provides the class 
:class:`fluiddyn.lab.probes.MovingConductivityProbe` which can be used like this:

.. code:: python

    # import the class representing the moving conductivity probe
    from fluiddyn.lab.probes import MovingConductivityProbe
    
    # create an instance of this class
    probe = MovingConductivityProbe()
    
    try:
        # set a parameter, the sample rate (in Hz)
        probe.set_sample_rate(2000)
    
        # just move the probe (in mm and mm/s)
        probe.move(deltaz=-100, speed=50)
    
        # just measure without moving (in s)
        measurements1 = probe.measure(duration=5)
    
        # move and measure (in mm and mm/s)
        measurements2 = probe.move_measure(deltaz=100, speed=100)
    except AttributeError:
        pass

Of course this is a very simple example and there are more options to create the object *probe* and for the functions. Look at the
documentation, i.e. in this case here: :class:`fluiddyn.lab.probes.MovingConductivityProbe`.

Save and load an object
-----------------------

For some classes of FluidDyn, the objects can be saved in a file and loaded afterwards. This is a very useful feature! To see how it works, we can consider the example of a tank filled with a stratified fluid, which is represented by the class
:class:`fluiddyn.lab.tanks.StratifiedTank`. Let's first see how we create a tank:

.. code:: python

    from fluiddyn.lab.tanks import StratifiedTank
    
    # create a tank with a linear stratification (see the doc of the class)
    tank = StratifiedTank(
        H=550, S=100, 
        z=[0, 500], rho=[1.1, 1])

The numerical object *tank* contains some information and can be use to do useful. We can for example fill the physical tank with the wanted profile (which makes use of some pumps also controlled by FluidDyn, see the class :class:`fluiddyn.lab.pumps.MasterFlexPumps`):

.. code:: python

    tank.fill()


.. parsed-literal::

    
    Warning: can not fill without pumps. It will only perform a test of
    the filling. To really fill the tank, set argument pumps to True or to
    an instance of class MasterFlexPumps.
    
    flowrate_tot: 840.00 ml/min
    vol_to_pump: 192.00 ml
    time for the filling:  0.23 min
    volume pumped / volume to pump = 0.9479
    The filling is finished.



.. image:: tuto_lab_user_files/tuto_lab_user_11_1.png



.. image:: tuto_lab_user_files/tuto_lab_user_11_2.png


The numerical object *tank* can be saved in a file tank.h5 with its
function *save* (the documentation explains how to control where the
file is saved):

.. code:: python

    if os.path.exists('/tmp/tank.h5'):
        os.remove('/tmp/tank.h5')

.. code:: python

    tank.save('/tmp')

If we come back some days later and we want to use again this particular instance of :class:`fluiddyn.lab.tanks.StratifiedTank`.
Let's assume that the file is in a directory ``/tmp/exp0``.  If we really know that this file contains the information for loading an object of :class:`fluiddyn.lab.tanks.StratifiedTank`, we can obtain the numerical representation of the tank by doing:

.. code:: python

    del(tank)
    tank = StratifiedTank(str_path='/tmp')

But most of the case, it is easier and safer to use the function :func:`fluiddyn.util.util.create_object_from_file` like this:

.. code:: python

    path_to_tank_h5 = '/tmp/tank.h5'
    tank = fld.create_object_from_file(path_to_tank_h5)

The function :func:`create_object_from_file` gets the correct class from information written in the file, calls the constructor of this class and return the object.

.. code:: python

    tank.profile.plot()



.. image:: tuto_lab_user_files/tuto_lab_user_20_0.png


Representation of an experiment
-------------------------------

Physically, an experiment consists in interacting objects.  The
experimentalist wants to control the actions of the objects with a
good control in space and time and in a reproducible way. The results
are then measurements produced by the measuring objects.  Usually,
after the experiment has been set up, it is repeated a number of times
in order to vary some parameters.

A experimental set-up is represented in FluidDyn by a class derived
from the class :class:`fluiddyn.lab.exp.base.Experiment`.  The
experiment class has attributes that represent the physical objects
interacting in the experimental set-up.

Each realisation of the experimental set-up (with a particular set of
parameters) is represented by an instance of the experiment
class. Each experiment (each realisation) is associated with a
particular directory.

In order to create a class, do for example:

.. code:: python

    from fluiddyn.lab.exp.taylorcouette.linearprofile import ILSTaylorCouetteExp
    
    exp = ILSTaylorCouetteExp(
        rho_max=1.1, N0=1., prop_homog=0.1,
        Omega1=0.4, Omega2=0, R1=150, R2=200,
        description="""This experiment is for the tutorial.""")
    
    [attr for attr in dir(exp) if not attr.startswith('_')]




.. parsed-literal::

    ['board',
     'description',
     'first_creation',
     'name_dir',
     'params',
     'path_save',
     'profiles',
     'save_script',
     'tank',
     'time_start']



.. code:: python

    print(exp.description)


.. parsed-literal::

    
    Experiment in a Taylor-Couette.
    
    This tank is 520 mm high. The radius of the outer cylinder is
    approximately   200 mm.
    
    
    Initially linear stratification (ILS)...
    
    This experiment is for the tutorial.


.. code:: python

    print(exp.path_save)


.. parsed-literal::

    /storage2/Dropbox/STC/Exp_data/TaylorCouette/ILS/Exp_Omega1=0.40_N0=1.00_2015-02-28_22-05-05


When this experiment has been created, the description files have been
automatically saved in the "right" place. This "right" place being
defined in the class of the experiment. Then we can easily reload the
experiment.

.. code:: python

    path_save = exp.path_save
    del(exp)
    exp = fld.load_exp(path_save[-20:-5])
    print(exp.path_save)
    print('R2 = {}'.format(exp.params['R2']))


.. parsed-literal::

    /storage2/Dropbox/STC/Exp_data/TaylorCouette/ILS/Exp_Omega1=0.40_N0=1.00_2015-02-28_22-05-05
    R2 = 200


Note that I deliberately only use the string
``path_save[-20:-5]`` to show that
:func:`fld.load_exp` is sufficiently clever to find out an experiment
that corresponds to this string. Be careful to provide a sufficiently
long string to be sure to load the wanted experiment.
