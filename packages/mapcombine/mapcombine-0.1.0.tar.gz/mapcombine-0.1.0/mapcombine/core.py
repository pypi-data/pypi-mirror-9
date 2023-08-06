"""
Parallel process model: does not require modification
"""

def outer_process(job):  
  """
  Process to be executed in the outer IPython.parallel map
  """

  # Split the arguments
  args, params, frame = job

  # always need these
  from importlib import import_module
  if args.MR_init is None:
    MR = import_module(args.mapreduce)
    args.MR_init = MR.MR_init
  if args.reduce is None:
    MR = import_module(args.mapreduce)
    args.reduce = MR.reduce_

  # Initialize the MapReduce data with base cases
  # Returns job list to pass to map
  jobs, base = args.MR_init(args, params, frame)

  # Map!
  import time as time_
  ttime = time_.time()
  if args.thread < 2:
    results = map(inner_process, jobs)
  else:
    from multiprocessing import Pool
    p = Pool(processes=args.thread)
    results = p.imap_unordered(inner_process, jobs, chunksize = 1)
  if args.verbose:
    print('  Map took {:f}s on {:d} processes'.format(time_.time()-ttime, args.thread))

  # Reduce!
  ttime = time_.time()
  for r in results:
    args.reduce(base, r)
  if args.thread >= 2:
    p.close()
  if args.verbose:
    print('  Reduce took {:f}s on {:d} processes'.format(time_.time()-ttime, args.thread))

  base["frame"] = frame
  # Analysis! 
  if args.post is not None:
    post = import_module(args.post)
    post.post_frame(base, params, args)

  return base


def inner_process(job):
  """
  Process to be executed  in the inner multiprocessing map
  """
  
  # Parse the arguments
  elm_range, params, args, ans_in = job

  # import Map and Reduce
  from importlib import import_module
  if args.map is None:
    args.map = import_module(args.mapreduce).map_
  if args.reduce is None:
    args.reduce = import_module(args.mapreduce).reduce_

  # Create 'empty' answer dictionary
  from copy import deepcopy
  res = ans_in
  ans = deepcopy(ans_in)

  # Loop over maps and local reduces
  for pos in range(elm_range[0], elm_range[1], args.block):
    # make sure we don't read past this thread's range
    nelm_to_read = min(args.block, elm_range[1] - pos)

    # All the work is here!
    args.map(pos, nelm_to_read, params, ans, pos + nelm_to_read == elm_range[1])

    # This reduce is more of a combiner
    args.reduce(res, ans)

  return res

