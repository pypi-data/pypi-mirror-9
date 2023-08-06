Dashboards
===============================================

Single Dashboard 
----------------

To initialize a single dashboard you need create a Dashboard object and pass valid options as shown below:

.. code-block:: javascript

    var dashboard = new Dashboard(options);

Where the `options` are a json object with the following specifications

**Options**

name `(optional)`
    The name of widget. *(default:* ``undefined`` *)*

viewportWidth `(optional)`
    Width of viewport where expected that the dashboard was displayed. *(default:* ``$(window).width()`` *)*

viewportHeight `(optional)`
    Height of viewport where expected that the dashboard was displayed. *(default:* ``$(window).height()`` *)*

widgetMargins `(optional)`
    Margin between each widget. *(default:* ``[5, 5]`` *)*

widgetBaseDimensions `(optional)`
    Default width and height of each widget in the dashboard. *(default:* ``[370, 340]`` *)*


**Dashboard methods**

name
    Return the name of the dashboard or **'unnamed'**.

show
    Show the dashboard (if it's hidden) and publish the event **shown** for this dashboard.

hide
    Show the dashboard (if it's showing) and publish the event **hidden** for this dashboard.

grid
    Return the *gridster* element for this dashboard.

activeWidgets
    Return the loaded widgets for this dashboard.

addWidget
    To add a new Widget, for example:

    .. code-block:: javascript

        myDashboard.addWidget('myWheaterWidget', 'Weather', {
            WOEID: 395269
        });

    For details you can check the `widgets topic`__

.. _WidgetsNamingConvention: widgets.html
__ WidgetsNamingConvention_

listWidgets
    Returns the list of widgets created on this dashboard

subscribe
    To subscribe an event in this dashboard you can doing as follow:

    .. code-block:: javascript

        myDashboard.subscribe('myEvent', function() {
            console.log('event fired!');
        });

publish
    To publish an event in this dashboard you can doing as follow:

    .. code-block:: javascript

        myDashboard.publish('myEvent');


Multiple Dashboards
-------------------

To initialize a multiple dashboards you need create a DashboardSet object and pass valid options as shown below:

.. code-block:: javascript

    var dashboardSet = new DashboardSet();



**DashboardSet methods**

addDashboard
    To add a new Dashboard:

    .. code-block:: javascript

        dashboardSet.addDashboard(name, options)


    Where `name` is a string with the name of dashboard and `options` is a json object with the same format of the options of the `Dashboard` object.

getDashboard
    To get a Dashboard from the DashboardSet object:

    .. code-block:: javascript

        dashboardSet.getDashboard(name)

**Swap between dashboards**

*Manual*

To swap between dashboards need to press the `ctrl` key to display the menu.

*Automatic*

To swap the dashboards automatically you can set the option `rollingChoices` as *true* when the dashboardSet is created as follows:

.. code-block:: javascript

    myDashboardSet = new DashboardSet({
        rollingChoices: true
    }),

Then you can select the rolling time in the `ctrl` menu.  Or you can add the parameter `roll=<value>` to the URL, where the value has to be specified in microseconds, for example:

::

    http://127.0.0.1:8000/dashboard/?roll=3000

**Dashboard Events**

Each single dashboard publish a **shown** or **hidden** event when the dashboard are loaded or unloaded, you can use it as follows:

.. code-block:: javascript

    myDashboard = myDashboardSet.addDashboard('New Dashboard')
    myDashboard.subscribe('shown', function() {alert('new dashboard shown')})
    myDashboard.subscribe('hidden', function() {alert('new dashboard hidden')})
