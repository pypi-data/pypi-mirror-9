from setuptools import setup, find_packages

def read_file(txt_file):
    with open(txt_file) as f:
        return f.read()

setup(name='emspring',
      version='0.83.1449',
      description='Electron Microscopy Single-Particle Based Helical Reconstruction',
      long_description=read_file('README.rst') + 2 * '\n' +  read_file('CHANGES.rst') + 2 * '\n' + read_file('license.txt'),
      keywords='Electron cryomicroscopy, cryo-EM, image processing, SPARX, EMAN2, Helical assembly, ' + \
      '3D reconstruction, helical symmetry',
      author='Carsten Sachse',
      author_email='carsten.sachse@gmail.com',
      url='http://www.sachse.embl.de/emspring',
      license='Modified BSD License',
    classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Operating System :: Unix',
    'Environment :: X11 Applications :: Qt',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python',
    'Topic :: Scientific/Engineering :: Image Recognition',
    ],

      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'numpy',
          'scipy',
          'visvis',
          'sqlalchemy',
          'tabulate',
          'pkginfo',
      ],
      entry_points = {
        'console_scripts': [
       # -*- Entry points: -*-
            'springenv = spring.csinfrastr.cslaunch:main',
            'spring = spring.springgui.spring_launch:main',
            'scansplit = spring.micprgs.scansplit:main',
            'scansplit_mpi = spring.micprgs.scansplit_mpi:main',
            # scanspring
            'micexam = spring.micprgs.micexam:main',
            'micexam_mpi = spring.micprgs.micexam_mpi:main',
            'micctfdetermine = spring.micprgs.micctfdetermine:main',
            'micctfdetermine_mpi = spring.micprgs.micctfdetermine_mpi:main',
            'michelixtrace = spring.micprgs.michelixtrace:main',
            'michelixtrace_mpi = spring.micprgs.michelixtrace_mpi:main',
            'scanlinefit = spring.micprgs.scanlinefit:main',
            'scandotfit = spring.micprgs.scandotfit:main',
            'scanrowcolcorr = spring.micprgs.scanrowcolcorr:main',
            # spring2d
            'segment = spring.segment2d.segment:main',
            'segment_mpi = spring.segment2d.segment_mpi:main',
            'segmentexam = spring.segment2d.segmentexam:main',
            'segmentexam_mpi = spring.segment2d.segmentexam_mpi:main',
            'segmentclass = spring.segment2d.segmentclass:main',
            'segmentalign2d = spring.segment2d.segmentalign2d:main',
            'segmentalign2d_mpi = spring.segment2d.segmentalign2d_mpi:main',
            'segclassexam = spring.segment2d.segclassexam:main',
            'segclassexam_mpi = spring.segment2d.segclassexam_mpi:main',
            'segclasslayer = spring.segment2d.segclasslayer:main',
            'seglayer2lattice = spring.segment2d.seglayer2lattice:main',
            'segmentplot = spring.segment2d.segmentplot:main',
            # spring3d
            'segclassreconstruct = spring.segment3d.segclassreconstruct:main',
            'segclassreconstruct_mpi = spring.segment3d.segclassreconstruct_mpi:main',
            'segmentrefine3d = spring.segment3d.refine.sr3d_main:main',
            'segmentrefine3d_mpi = spring.segment3d.refine.sr3d_mpi:main',
            'segrefine3dgrid = spring.segment3d.segrefine3dgrid:main',
            'seggridexplore = spring.segment3d.seggridexplore:main',
            'segrefine3dplot = spring.segment3d.segrefine3dplot:main',
            'segrefine3dcyclexplore = spring.segment3d.segrefine3dcyclexplore:main',
            'segrefine3dinspect = spring.segment3d.segrefine3dinspect:main',
            'segclassmodel = spring.segment3d.segclassmodel:main',
            'segclassmodel_mpi = spring.segment3d.segclassmodel_mpi:main',
            'segmultirefine3d= spring.segment3d.segmultirefine3d:main',
            'segmultirefine3d_mpi = spring.segment3d.segmultirefine3d_mpi:main',
            # particle
            'particlestack = spring.particle2d.particlestack:main',
            'particleclass = spring.particle2d.particleclass:main',
            'particlealign2d = spring.particle2d.particlealign2d:main',
            'particlealign2d_mpi = spring.particle2d.particlealign2d_mpi:main'
        ]

    }
      )
