conda activate drone-fly
# python src/droneFly/main.py --config=exp_multi-diff.yaml --flight-file=move_forth-back.csv
python src/droneFly/main.py --config=exp_multi-diff.yaml --flight-file=move_stationary.csv #--plot
# python src/droneFly/main.py --config=exp_norm.yaml -f=move_stationary.csv -d