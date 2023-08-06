>>> from sinusoid import SinusoidModel

# there are three ways to set up the model:

# 1. when you create the model

>>> a_model = SinusoidModel(frequencies=[1.2, 2.3], modes=[[1, 0], [0, 1], [1, 1]])

# note that each mode is a list (or a tuple or a numpy array) with two
# elements, one for each frequency.

# frequencies and modes are immutable 

>>> a_model.frequencies
(1.2, 2.3)
>>> a_model.modes
((1, 0), (0, 1), (1, 1))

# The number of components of each mode must match the number of 
# frequencies:

>>> bad_model = SinusoidModel(frequencies=[1.2, 2.3], modes=[[1, 0, 0]])
Traceback (most recent call last):
    ...
ValueError: Wrong number of modes in mode setter for mode [1, 0, 0]

# 2. After you create the model by adding frequencies and modes

>>> another_model = SinusoidModel()
>>> another_model.add_frequency(1.2, 2.3)
>>> another_model.frequencies
(1.2, 2.3)
>>> another_model.modes
()
>>> another_model.add_mode(1, 0)  # add modes one at a time, or...
>>> another_model.modes
((1, 0),)
>>> another_model.add_mode([0, 1], [1, 1])  # several at a time
>>> another_model.modes
((1, 0), (0, 1), (1, 1))

# 3. Create a new model using another model as initializer

>>> import copy
>>> a_model_extended = copy.deepcopy(a_model)

# Changing a model

>>> a_model_extended.add_frequency(3.4)

# Adding a frequency when modes already exist adds a weight of zero
# to the new frequency

>>> a_model_extended.modes
((1, 0, 0), (0, 1, 0), (1, 1, 0))

# this behavior can be prevented by setting the appropriate keyword

>>> a_model_extended = copy.deepcopy(a_model)
>>> a_model_extended.add_frequency(3.4, extend_modes=False)

# in this case all of the modes are simply deleted:

>>> a_model_extended.modes
()

# 
# Note that you can change the values of the frequencies by simply
# setting the frequency:
#

>>> a_model_extended = copy.deepcopy(a_model)
>>> a_model_extended.frequencies
(1.2, 2.3)
>>> a_model_extended.frequencies = (7.8, 3.5)
>>> a_model_extended.frequencies
(7.8, 3.5)

# You CANNOT change the number of frequencies by setting the frequency 
# property--you must use add_frequency to increase the number of frequencies;
# to decrease the number of frequencies you must define a new model.
#

>>> a_model_extended.frequencies = [1.1, 2.3, 4.5]
Traceback (most recent call last):
    ...
ValueError: Use method add_frequency to increase the number of frequencies

>>> a_model_extended.frequencies = [1.5]
Traceback (most recent call last):
    ...
ValueError: Cannot decrease number of frequencies. Define a new model instead.

#
#  adding duplicate modes or frequencies.
#

# an error is generated when trying to add a frequency already in the model.

>>> a_model_extended.frequencies
(7.8, 3.5)
>>> a_model_extended.add_frequency(7.8)
Traceback (most recent call last):
    ...
ValueError: The frequencies 7.8 are already in the model
>>> a_model_extended.frequencies = [7.8, 1.5]
Traceback (most recent call last):
    ...
ValueError: The frequencies 7.8 are already in the model
 
 # an error is also generated when trying to add a mode already in the model

>>> a_model_extended.modes
((1, 0), (0, 1), (1, 1))
>>> a_model_extended.add_mode(1, 0)
Traceback (most recent call last):
    ...
ValueError: Mode (1, 0) is already in the model; model is unchanged

