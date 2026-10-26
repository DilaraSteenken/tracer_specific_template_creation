# tracer specific template creation 
- We first register the PET images to their corresponding CT images if exist
- The CT registered PET images are then rigidly registered to a selected single animal images (scanned with the preferred tracer as all PET images)
- These images are then averaged and smoothed
- With this template we can then register all raw PET images to the template and then create a mask based on the template for brain cropping.
