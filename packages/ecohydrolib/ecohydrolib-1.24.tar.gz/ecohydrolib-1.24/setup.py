from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='ecohydrolib',
      version='1.24',
      description='Libraries and command-line scripts for performing ecohydrology data preparation workflows.',
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
      url='https://github.com/selimnairb/EcohydroLib',
      author='Brian Miles',
      author_email='brian_miles@unc.edu',
      license='BSD',
      packages=['ecohydrolib', 
                'ecohydrolib.climatedata',
                'ecohydrolib.command',
                'ecohydrolib.geosciaus',
                'ecohydrolib.hydro1k',
                'ecohydrolib.nhdplus2',
                'ecohydrolib.nlcd',
                'ecohydrolib.solim',
                'ecohydrolib.spatialdata',
                'ecohydrolib.ssurgo',
                'ecohydrolib.tests',
                'ecohydrolib.wcs4dem' 
                ],
      install_requires=[
        #'GDAL', # GDAL does not build under OS X easy_install/PIP
        'pyproj',
        'numpy',
        'owslib>=0.8.12',
        'oset',
        'httplib2',
        'shapely'
      ],
      scripts=['bin/DumpClimateStationInfo.py',
               'bin/DumpMetadataToiRODSXML.py',
               'bin/GenerateSoilPropertyRastersFromSOLIM.py',
               'bin/GenerateSoilPropertyRastersFromSSURGO.py',
               'bin/GetBoundingboxFromStudyareaShapefile.py',
               'bin/GetCatchmentShapefileForHYDRO1kBasins.py',
               'bin/GetCatchmentShapefileForNHDStreamflowGage.py',
               'bin/GetDEMExplorerDEMForBoundingbox.py',
               'bin/GetGADEMForBoundingBox.py',
               'bin/GetGHCNDailyClimateDataForBoundingboxCentroid.py',
               'bin/GetGHCNDailyClimateDataForStationsInBoundingbox.py',
               'bin/GetHYDRO1kDEMForBoundingbox.py',
               'bin/GetNHDStreamflowGageIdentifiersAndLocation.py',
               'bin/GetNLCDForDEMExtent.py',
               'bin/GetSoilGridAustralia.py',
               'bin/GetSSURGOFeaturesForBoundingbox.py',
               'bin/RegisterDEM.py',
               'bin/RegisterGage.py',
               'bin/RegisterRaster.py',
               'bin/RegisterStudyAreaShapefile.py',
               'bin/RunCmd.py',
               'bin/GHCNDSetup/GHCNDSetup.py',
               'bin/NHDPlusV2Setup/NHDPlusV2Setup.py',
               'cgi/GetCatchmentFeaturesForStreamflowGage',
               'cgi/LocateStreamflowGage'
      ],
      zip_safe=False)
