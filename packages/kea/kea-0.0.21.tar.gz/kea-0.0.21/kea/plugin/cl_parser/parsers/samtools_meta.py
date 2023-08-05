meta = {'regions': {'pattern': '/\\S+/', 'type': 'other'}, 'frac_subsample': {'pattern': '-s <float>', 'type': 'option', 'name': 'frac_subsample'}, 'no_threads': {'pattern': '-@ <int>', 'type': 'option', 'name': 'no_threads'}, 'bedoverlap': {'category': 'input', 'pattern': 'file', 'type': 'file'}, 'output_is_bam': {'pattern': '-b', 'type': 'flag', 'name': 'output_is_bam'}, 'input_is_sam': {'pattern': '-S', 'type': 'flag', 'name': 'input_is_sam'}, 'output_header': {'pattern': '-h', 'type': 'flag', 'name': 'output_header'}, 'sort_dasho': {'pattern': '"-o"', 'type': 'other'}, 'prefix_is_fullname': {'pattern': '-f', 'type': 'flag', 'name': 'prefix_is_fullname'}, 'outputfile': {'category': 'output', 'default': '__stdout__', 'cardinality': '1', 'type': 'file', 'pattern': '/\\S+\\.bam/'}, 'compression_level': {'pattern': '-l <int>', 'type': 'option', 'name': 'compression_level'}, 'outprefix': {'pattern': '/\\S+/', 'cardinality': '1', 'type': 'other'}, 'sort_by_read': {'pattern': '-n', 'type': 'flag', 'name': 'sort_by_read'}, 'inputfile': {'category': 'input', 'pattern': '/\\S+\\.[bs]am/', 'type': 'file'}, 'output_to_stdout': {'pattern': '-o', 'type': 'flag', 'name': 'output_to_stdout'}, 'thread_memory': {'pattern': '-m <string>', 'type': 'option', 'name': 'thread_memory'}}