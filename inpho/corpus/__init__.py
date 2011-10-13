import inpho

# get corpus path
path = inpho.config.get('corpus', 'path')

# set up data paths
occur_path = inpho.config.get_data_path('occur', 'corpus')
fuzzy_path = inpho.config.get_data_path('fuzzy', 'corpus')
sql_path = inpho.config.get_data_path('sql', 'corpus')

    
