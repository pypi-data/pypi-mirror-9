import compare_tools
import bayesian_learner
#compare_tools.random_delete("Training_Features.csv","tf_removed.csv")
bf= bayesian_learner.bayesian_fill(min_iterations=8,max_iterations=80,pvalparam=0.3)
#bf=bayesian_learner.bayesian_fill(min_iterations=5,max_iterations=10)
bf.fill_missing_data("tf_removed.csv","filled_by_now.txt")
bf.json_network()

compare_tools.compare_predictions("tf_removed.csv","Training_Features.csv","filled_by_now.txt")

