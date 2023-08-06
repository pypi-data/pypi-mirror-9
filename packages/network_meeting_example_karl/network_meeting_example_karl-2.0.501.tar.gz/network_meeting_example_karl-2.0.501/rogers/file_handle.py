

class File_handle():
    def __init__(self, filename):
        self.filename = filename
        self.edge_count = 0
        self.node_count = 0
        self.average_value = 0
        
    def parse(self):
        nodes = []
        total = 0
        with open(self.filename, 'r') as infile:
            for line in infile:
                self.edge_count += 1
                line = (line.strip()).split('\t')
                nodes += [line[0], line[1]]
                total += float(line[2])
        self.node_count = len(list(set(nodes)))
        self.average_value = total / float(self.node_count)
        return 
    
    def export(self, outfilename):
        with open(outfilename, 'w') as outfile:
            outfile.write('edge count:\t'+str(self.edge_count)+'\n')
            outfile.write('node count:\t'+str(self.node_count)+'\n')
            outfile.write('average edge value:\t'+str(self.average_value)+'\n')
        return