from inpho.model import Session
# TODO: Examine proper encapsulation

class GraphEdge(object):
    def __str__(self):
        return  "%s\t%s\t%s\t%s" % (self.ante_id, self.cons_id, self.weight, self.jweight)
    
    def __repr__(self):
        return "<GraphEdge: %s -> %s (jweight %s)>" % (self.ante_id, self.cons_id, self.jweight)

    def json_struct(self):
        struct = { 'ante' : self.ante_id, 
                  'cons' : self.cons_id,
                  'weight' : self.weight, 
                  'jweight' : self.jweight}
        return struct

class IdeaGraphEdge(GraphEdge):
    @staticmethod
    def get_subgraph(ids, thresh=None):
        edge_q = Session.query(IdeaGraphEdge)
        edge_q = edge_q.order_by(IdeaGraphEdge.jweight.desc())
        edge_q = edge_q.filter(IdeaGraphEdge.cons_id.in_(ids))
        edge_q = edge_q.filter(IdeaGraphEdge.ante_id.in_(ids))
        if thresh:
            edge_q = edge_q.filter(IdeaGraphEdge.jweight > thresh)
        return edge_q.all()

class IdeaThinkerGraphEdge(GraphEdge):
    pass

class ThinkerGraphEdge(GraphEdge):
    pass
