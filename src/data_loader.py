import jams
import jams.display

# load annotation data
def load_annotations(path):
    J = jams.load(path+'00_BN1-129-Eb_comp.jams')
    for a in J.annotations:
        if(a.namespace=='note_midi'):
            jams.display.display(a)








if __name__=='__main__':
    path = 'e:/workspace/guitar_set/annotation/'
    data = load_annotations(path)