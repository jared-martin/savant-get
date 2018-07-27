# ⚾ savant-get
Go get all that data from Baseball Savant

## Install
First clone or [download](https://github.com/jared-martin/savant-get.git) the repository:
```
$ git clone https://github.com/jared-martin/savant-get.git ~/Downloads/savant-get-master
```

Now you can run the script straight away:
```
$ python ~/Downloads/savant-get-master/savant_get.py
```

Or you can install and run the CLI:
```
$ cd ~/Downloads/savant-get-master/
$ python setup.py install
$ savant-get
```

## Use
Run it without any arguments to start downloading from the last date downloaded previously (or the start of the Statcast era if you haven't downloaded anything yet):
```
$ savant-get
```

Run it with one argument to start downloading from a specific date:
```
$ savant-get 2018-04-02
```

Run it with two arguments to start downloading from a specific date and stop on another date:
```
$ savant-get 2018-04-02 2018-07-15
```

Run it with `-v` to display verbose logging:
```
$ savant-get -v 2018-02-26 2018-02-28
DEBUG:root:Directory of files: /Users/jared/baseball-savant-files
DEBUG:root:Starting on the day passed as the first argument: 2018-02-26
DEBUG:root:Ending on the day passed as the second argument: 2018-02-28
DEBUG:root:Getting url: https://baseballsavant.mlb.com/statcast_search/csv?all=true&batter_stands=&game_date_gt=2018-02-26&game_date_lt=2018-02-28&group_by=name&hfAB=&hfBBL=&hfBBT=&hfC=&hfFlag=&hfGT=R%7CPO%7CS%7C&hfInn=&hfNewZones=&hfOuts=&hfPR=&hfPT=&hfRO=&hfSA=&hfSea=2018%7C&hfSit=&hfZ=&home_road=&metric_1=&min_abs=0&min_pitches=0&min_results=0&opponent=&pitcher_throws=&player_event_sort=h_launch_speed&player_type=batter&position=&sort_col=pitches&sort_order=desc&stadium=&team=&type=details
DEBUG:root:Response status code: 200
/Users/jared/baseball-savant-files/baseball-savant-2018-02-28.csv
/Users/jared/baseball-savant-files/baseball-savant-2018-02-27.csv
/Users/jared/baseball-savant-files/baseball-savant-2018-02-26.csv
```

### Data directory
By default, the script creates files in your current working directory.  You can change this by setting the environment variable `BASEBALL_SAVANT_DATA_DIR`:
```
$ export BASEBALL_SAVANT_DATA_DIR=~/Downloads/
$ savant-get -v
DEBUG:root:Directory of files: /Users/jared/Downloads
DEBUG:root:Starting on the day after the last day downloaded: 2018-07-24
DEBUG:root:Ending on yesterday: 2018-07-25
DEBUG:root:Getting url: https://baseballsavant.mlb.com/statcast_search/csv?all=true&batter_stands=&game_date_gt=2018-07-24&game_date_lt=2018-07-25&group_by=name&hfAB=&hfBBL=&hfBBT=&hfC=&hfFlag=&hfGT=R%7CPO%7CS%7C&hfInn=&hfNewZones=&hfOuts=&hfPR=&hfPT=&hfRO=&hfSA=&hfSea=2018%7C&hfSit=&hfZ=&home_road=&metric_1=&min_abs=0&min_pitches=0&min_results=0&opponent=&pitcher_throws=&player_event_sort=h_launch_speed&player_type=batter&position=&sort_col=pitches&sort_order=desc&stadium=&team=&type=details
DEBUG:root:Response status code: 200
/Users/jared/Downloads/baseball-savant-2018-07-25.csv
/Users/jared/Downloads/baseball-savant-2018-07-24.csv
```

## What next?
Try pairing with SQLite for a full-bodied, vibrant blend of baseball and data analysis.  Since the script prints the full path to each file it creates, its output can be read in a loop and loaded into a table like so:
```
$ savant-get | while read file_path; do sqlite3 -separator , /path/to/sqlite/database.sqlite3 ".import ${file_path} baseball_savant"; done
```

If that sounds like your idea of a good time, here's some DDL to get you started:
```
$ sqlite3 /path/to/sqlite/database.sqlite3 <<EOF
CREATE TABLE baseball_savant (
    pitch_type TEXT
  , game_date TEXT
  , release_speed FLOAT
  , release_pos_x FLOAT
  , release_pos_z FLOAT
  , player_name TEXT
  , batter TEXT
  , pitcher TEXT
  , events TEXT
  , description TEXT
  , spin_dir TEXT
  , spin_rate_deprecated TEXT
  , break_angle_deprecated TEXT
  , break_length_deprecated TEXT
  , zone INTEGER
  , des TEXT
  , game_type TEXT
  , stand TEXT
  , p_throws TEXT
  , home_team TEXT
  , away_team TEXT
  , type TEXT
  , hit_location INTEGER
  , bb_type TEXT
  , balls INTEGER
  , strikes INTEGER
  , game_year INTEGER
  , pfx_x FLOAT
  , pfx_z FLOAT
  , plate_x FLOAT
  , plate_z FLOAT
  , on_3b TEXT
  , on_2b TEXT
  , on_1b TEXT
  , outs_when_up INTEGER
  , inning INTEGER
  , inning_topbot TEXT
  , hc_x FLOAT
  , hc_y FLOAT
  , tfs_deprecated TEXT
  , tfs_zulu_deprecated TEXT
  , pos2_person_id_ TEXT
  , umpire TEXT
  , sv_id TEXT
  , vx0 FLOAT
  , vy0 FLOAT
  , vz0 FLOAT
  , ax FLOAT
  , ay FLOAT
  , az FLOAT
  , sz_top FLOAT
  , sz_bot FLOAT
  , hit_distance_sc INTEGER
  , launch_speed FLOAT
  , launch_angle FLOAT
  , effective_speed FLOAT
  , release_spin_rate INTEGER
  , release_extension FLOAT
  , game_pk TEXT
  , pos1_person_id TEXT
  , pos2_person_id TEXT
  , pos3_person_id TEXT
  , pos4_person_id TEXT
  , pos5_person_id TEXT
  , pos6_person_id TEXT
  , pos7_person_id TEXT
  , pos8_person_id TEXT
  , pos9_person_id TEXT
  , release_pos_y FLOAT
  , estimated_ba_using_speedangle FLOAT
  , estimated_woba_using_speedangle FLOAT
  , woba_value FLOAT
  , woba_denom FLOAT
  , babip_value FLOAT
  , iso_value FLOAT
  , launch_speed_angle INTEGER
  , at_bat_number INTEGER
  , pitch_number INTEGER
  , pitch_name TEXT
  , home_score INTEGER
  , away_score INTEGER
  , bat_score INTEGER
  , fld_score INTEGER
  , post_away_score INTEGER
  , post_home_score INTEGER
  , post_bat_score INTEGER
  , post_fld_score INTEGER
  , if_fielding_alignment TEXT
  , of_fielding_alignment TEXT
  , PRIMARY KEY (game_pk, at_bat_number, pitch_number, pfx_x, pfx_z)
);
EOF
```
