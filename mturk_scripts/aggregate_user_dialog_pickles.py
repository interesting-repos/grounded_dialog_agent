#!/usr/bin/env python
__author__ = 'jesse'

import argparse
import pickle
import os


def main():

    summary_csv_fn = FLAGS_summary_csv
    user_data_dir = FLAGS_user_data_dir
    outfile = FLAGS_outfile

    agg_role_utterances_role_chosen_pairs = []
    agg_perceptual_labels = []
    agg_perceptual_synonymy = []
    num_users = 0
    num_correct_tasks = 0
    with open(summary_csv_fn, 'r') as f:
        lines = f.readlines()
        headers = lines[0].strip().split(',')
        for lidx in range(1, len(lines)):
            data = lines[lidx].strip().split(',')

            uid = data[headers.index("uid")]
            pickle_exists = data[headers.index("pickle_exists")]
            if pickle_exists == "1":

                # Load user data from log pickle.
                pickle_fn = os.path.join(user_data_dir, uid + ".pickle")
                with open(pickle_fn, 'rb') as pickle_f:
                    actions_confirmed, utterances_by_role, new_perceptual_labels, perceptual_pred_synonymy = \
                        pickle.load(pickle_f)

                    tasks_correct = [True if data[headers.index("task_" + str(task) + "_correct")] == "1" else False
                                     for task in range(1, 4)]
                    for task in range(1, 4):
                        idx = task - 1
                        # If task was correct, note this user's data for inclusion in aggregated pickle.
                        if tasks_correct[idx]:
                            agg_role_utterances_role_chosen_pairs.append((actions_confirmed[idx],
                                                                          utterances_by_role[idx]))
                            num_correct_tasks += 1

                    # Regardless of correctness, record perceptual labels gathered from this user.
                    agg_perceptual_labels.extend(new_perceptual_labels)
                    agg_perceptual_synonymy.extend(perceptual_pred_synonymy)
                    num_users += 1

    if num_users == 0:
        print "ERROR: found no users"
        return 1

    # Report.
    print ("main: aggregated data from " + str(num_users) + " users and " + str(num_correct_tasks) + " tasks for an " +
           "average tasks per user of " + str(num_correct_tasks / float(num_users)))
    print ("main: this resulted in " + str(len(agg_role_utterances_role_chosen_pairs)) +
           " pairs of confirmed actions with dialog utterances per role")
    print ("main: for perception, this gives " + str(len(agg_perceptual_labels)) + " new perceptual labels over " +
           str(len(set([pred for pred, _, _ in agg_perceptual_labels]))) + " predicates")
    print ("main: for synonymy, this gives " + str(len(agg_perceptual_synonymy)) + " new synonymy relationship labels")

    # Record.
    with open(outfile, 'wb') as f:
        d = [agg_role_utterances_role_chosen_pairs, agg_perceptual_labels, agg_perceptual_synonymy]
        pickle.dump(d, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--summary_csv', type=str, required=True,
                        help="the summary csv generated by approve_mturk.py to aggregate users over")
    parser.add_argument('--user_data_dir', type=str, required=True,
                        help="where user data was stored during experiment")
    parser.add_argument('--outfile', type=str, required=True,
                        help="the outfile pickle to store the aggregated data")
    args = parser.parse_args()
    for k, v in vars(args).items():
        globals()['FLAGS_%s' % k] = v
    main()