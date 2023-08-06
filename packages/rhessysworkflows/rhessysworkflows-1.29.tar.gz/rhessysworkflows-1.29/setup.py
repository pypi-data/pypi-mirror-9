from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='rhessysworkflows',
      version='1.29',
      description='Libraries and command-line scripts for performing RHESSys data preparation workflows.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Topic :: Scientific/Engineering :: GIS'        
      ],
      url='https://github.com/selimnairb/RHESSysWorkflows',
      author='Brian Miles',
      author_email='brian_miles@unc.edu',
      license='BSD',
      packages=['rhessysworkflows',
                'rhessysworkflows.command',
                'rhessysworkflows.tests'
                ],
      install_requires=[
        'ecohydrolib>=1.19',
        'numpy>=1.7',
        'matplotlib>=1.1',
        'pandas',
        'scipy',
        'patsy',
        'statsmodels'
      ],
      scripts=['bin/CreateFlowtable.py',
               'bin/CreateFlowtableMultiple.py',
               'bin/CreateGRASSLocationFromDEM.py',
               'bin/CreateWorldfile.py',
               'bin/CreateWorldfileMultiple.py',
               'bin/DelineateWatershed.py',
               'bin/GenerateBaseStationMap.py',
               'bin/GenerateCustomSoilDefinitions.py',
               'bin/GenerateLandcoverMaps.py',
               'bin/GeneratePatchMap.py',
               'bin/GenerateSoilTextureMap.py',
               'bin/GenerateWorldTemplate.py',
               'bin/ImportClimateData.py',
               'bin/ImportRasterMapIntoGRASS.py',
               'bin/ImportRHESSysSource.py',
               'bin/PatchToCumulativeMap.py',
               'bin/PatchToCumulativeValues.py',
               'bin/PatchToMap.py',
               'bin/PatchToMovie.py',
               'bin/PatchZonalStats.py',
               'bin/PatchZonalStatsNormalize.py',
               'bin/RegisterCustomSoilReclassRules.py',
               'bin/RegisterLandcoverReclassRules.py',
               'bin/RHESSysPlot.py',
               'bin/RHESSysPlotMassbalance.py',
               'bin/RunLAIRead.py',
               'bin/RunLAIReadMultiple.py',
               'bin/RunModel.py'
      ],
      data_files=[('rhessysworkflows/etc/NLCD2006', ['etc/NLCD2006/impervious.rule',
                           'etc/NLCD2006/lai-recode.rule',
                           'etc/NLCD2006/landuse.rule',
                           'etc/NLCD2006/road.rule',
                           'etc/NLCD2006/stratum.rule'] ),
                  ('rhessysworkflows/etc/r.soils.texture', ['etc/r.soils.texture/FAO.dat',
                                                           'etc/r.soils.texture/isss.dat',
                                                           'etc/r.soils.texture/USDA.dat'] )
                  ],
                 
      zip_safe=False)
