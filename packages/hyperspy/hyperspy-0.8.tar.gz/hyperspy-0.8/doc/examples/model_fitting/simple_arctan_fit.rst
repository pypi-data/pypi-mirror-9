.. _model_fitting-simple_arctan_fit:

model_fitting example code: simple_arctan_fit.py
================================================

[`source code <simple_arctan_fit.py>`_]

::

    """Creates a spectrum, and fits an arctan to it."""
    
    import numpy as np
    
    # Generate the data and make the spectrum
    s = signals.SpectrumSimulation(
        np.arctan(np.arange(-500, 500)))
    s.axes_manager[0].offset = -500
    s.axes_manager[0].units = ""
    s.axes_manager[0].name = "x"
    s.metadata.General.title = "Simple arctan fit"
    
    s.add_gaussian_noise(0.1)
    
    # Make the arctan component for use in the model
    arctan_component = components.Arctan()
    
    # Create the model and add the arctan component
    m = create_model(s)
    m.append(arctan_component)
    
    # Fit the arctan component to the spectrum
    m.fit()
    
    # Print the result of the fit
    m.print_current_values()
    
    # Plot the spectrum and the model fitting
    m.plot()
    

Keywords: hyperspy, example, codex (see :ref:`how-to-search-examples`)