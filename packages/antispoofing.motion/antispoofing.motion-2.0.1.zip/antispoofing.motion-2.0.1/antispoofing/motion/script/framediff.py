#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 02 Aug 2010 11:31:31 CEST 

"""Calculates the normalized frame differences for face and background, for all
input videos. This technique is described on the paper: Counter-Measures to
Photo Attacks in Face Recognition: a public database and a baseline, Anjos &
Marcel, IJCB'11."""

import os, sys
import argparse
import string
import bob.io.video
import bob.ip.color

def main():
  
  import numpy

  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  INPUTDIR = os.path.join(basedir, 'database')
  OUTPUTDIR = os.path.join(basedir, 'framediff')

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-m', '--mininum-face-size', dest='min_face_size', 
      metavar='PIXELS', type=int, default=0,
      help='Minimum face size to be considered when pre-processing and extrapolating detections (defaults to %(default)s)')
  parser.add_argument('inputdir', metavar='DIR', type=str, default=INPUTDIR,
      nargs='?', help='Base directory containing the videos to be treated by this procedure (defaults to "%(default)s")')
  parser.add_argument('outputdir', metavar='DIR', type=str, default=OUTPUTDIR,
      nargs='?', help='Base output directory for every file created by this procedure defaults to "%(default)s")')
  parser.add_argument('-e', '--enrollment', action='store_true', default=False, dest='enrollment', help='If True, will do the processing of the enrollment data of the database (defaults to "%(default)s")')

  # The next option just returns the total number of cases we will be running
  # It can be used to set jman --array option. To avoid user confusion, this
  # option is suppressed # from the --help menu
  parser.add_argument('--grid-count', dest='grid_count', action='store_true',
      default=False, help=argparse.SUPPRESS)

  # Adds database support using the common infrastructure
  # N.B.: Only databases with 'video' support
  import antispoofing.utils.db 
  antispoofing.utils.db.Database.create_parser(parser, 'video')

  args = parser.parse_args()
  database = args.cls(args)

  # checks face sizes
  if args.min_face_size < 0:
    parser.error('Face size cannot be less than zero. Give a value in pixels')

  from antispoofing.utils.faceloc import preprocess_detections
  from .. import eval_face_differences, eval_background_differences

  # Creates an instance of the database
  db = args.cls(args)


  if args.enrollment:  
    process = database.get_enroll_data()
  else:  
    realObjects, attackObjects = database.get_all_data()
    process = realObjects + attackObjects 
    

  if args.grid_count:
    print len(process)
    sys.exit(0)
 
  # if we are on a grid environment, just find what I have to process.
  if os.environ.has_key('SGE_TASK_ID'):
    pos = int(os.environ['SGE_TASK_ID']) - 1
    if pos >= len(process):
      raise RuntimeError, "Grid request for job %d on a setup with %d jobs" % \
          (pos, len(process))
    process = [process[pos]]

  counter = 0
  for obj in process:
    counter += 1
 
    filename = obj.videofile(args.inputdir)
    input = bob.io.video.reader(filename)

    if string.find(database.short_description(), "CASIA") != -1:
      facefile = obj.facefile()
    else:
      facefile = obj.facefile(args.inputdir)

    locations = preprocess_detections(facefile, len(input), 
        facesize_filter=args.min_face_size)

    sys.stdout.write("Processing file %s (%d frames) [%d/%d]..." % (filename,
      input.number_of_frames, counter, len(process)))

    # start the work here...
    vin = input.load() # load all in one shot.
    prev = bob.ip.color.rgb_to_gray(vin[0,:,:,:])
    curr = numpy.empty_like(prev)
    data = numpy.zeros((len(vin), 2), dtype='float64')
    data[0] = (numpy.NaN, numpy.NaN)

    for k in range(1, vin.shape[0]):
      bob.ip.color.rgb_to_gray(vin[k,:,:,:], curr)

      if locations[k] and locations[k].is_valid():
        sys.stdout.write('.')
        data[k][0] = eval_face_differences(prev, curr, locations[k])
        data[k][1] = eval_background_differences(prev, curr, locations[k], None)
      else:
        sys.stdout.write('x')
        data[k] = (numpy.NaN, numpy.NaN)

      sys.stdout.flush()

      # swap buffers: curr <=> prev
      tmp = prev
      prev = curr
      curr = tmp

    obj.save(data, args.outputdir, '.hdf5')
    
    sys.stdout.write('\n')
    sys.stdout.flush()

  return 0

if __name__ == "__main__":
  main()
