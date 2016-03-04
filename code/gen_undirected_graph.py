import itertools
import sys
from sets import Set
import csv

csv_filename = 'strong_corrs_for_undirected_graph.csv'
undirected_graph_filename = 'undirected.dot'

channel_names = Set()

positive_pairs = Set()
negative_pairs = Set()
paired_nodes = Set()

with open(csv_filename, 'rb') as csvfile:
    csv_reader = csv.DictReader(csvfile)

    header_skipped = False
    for row in csv_reader:
        row_name = row['']
        # Go through all of the different columns and create connections if necessary
        for key in row.keys():
            if key != '' and row_name != key:
                if row[key] == 'P':
                    print "Positive correlation between %s and %s." % (row_name, key)
                    positive_pairs.add(Set([row_name, key]))
                    paired_nodes.add(row_name)
                    paired_nodes.add(key)
                elif row[key] == 'N':
                    print "Negative correlation between %s and %s." % (row_name, key)
                    negative_pairs.add(Set([row_name, key]))
                    paired_nodes.add(row_name)
                    paired_nodes.add(key)
                elif row[key] == '':
                    # print "No strong correlation between %s and %s." % (row_name, key)
                    pass
                else:
                    print "Undefined correlation between %s and %s!!!" % (row_name, key)

# Now, let's print out to the graph file
with open(undirected_graph_filename, 'w') as outfile:
    outfile.write('graph {\n')
    outfile.write('node [shape=ellipse];\n\n')
    outfile.write('// nodes\n')
    for node in paired_nodes:
        outfile.write(node + ' ');
    outfile.write(';\n\n')
    outfile.write('// positive edges\n')
    outfile.write('edge [color=Orange];\n')
    for positive_pair in positive_pairs:
        node1, node2 = list(positive_pair)
        outfile.write(node1 + ' -- ' + node2 + ';\n')
    outfile.write('\n// negative edges\n')
    outfile.write('edge [color=Blue];\n')
    for negative_pair in negative_pairs:
        node1, node2 = list(negative_pair)
        outfile.write(node1 + ' -- ' + node2 + ';\n')


    outfile.write('}')