PAGERANK_QUERY = """
CREATE OR REPLACE DISTRIBUTED QUERY tg_pagerank (STRING v_type, STRING e_type,
  FLOAT max_change=0.001, INT maximum_iteration=25, FLOAT damping=0.85, INT top_k = 100,
  BOOL print_results = TRUE, STRING result_attribute =  "", STRING file_path = "",
  BOOL display_edges = FALSE) SYNTAX V1 {

  TYPEDEF TUPLE<VERTEX Vertex_ID, FLOAT score> Vertex_Score;
  HeapAccum<Vertex_Score>(top_k, score DESC) @@top_scores_heap;
  SetAccum<VERTEX> @@top_vertices;      # vertices with top score
  MaxAccum<FLOAT> @@max_diff = 9999;    # max score change in an iteration
  SumAccum<FLOAT> @sum_recvd_score = 0; # sum of scores each vertex receives FROM neighbors
  SumAccum<FLOAT> @sum_score = 1;           # initial score for every vertex is 1.
  SetAccum<EDGE> @@edge_set;             # list of all edges, if display is needed
  FILE f (file_path);

  # PageRank iterations	
  Start = {v_type};                     # Start with all vertices of specified type(s)
  WHILE @@max_diff > max_change 
      LIMIT maximum_iteration DO
          @@max_diff = 0;
      V = SELECT s
  	FROM Start:s -(e_type:e)- v_type:t
  	ACCUM 
              t.@sum_recvd_score += s.@sum_score/(s.outdegree(e_type)) 
  	POST-ACCUM 
              s.@sum_score = (1.0-damping) + damping * s.@sum_recvd_score,
  	    s.@sum_recvd_score = 0,
  	    @@max_diff += abs(s.@sum_score - s.@sum_score');
  END; # END WHILE loop

  # Output
  IF file_path != "" THEN
      f.println("Vertex_ID", "PageRank");
  END;
  V = SELECT s 
      FROM Start:s
      POST-ACCUM 
          IF result_attribute != "" THEN 
              s.setAttr(result_attribute, s.@sum_score) 
          END,
  	IF file_path != "" THEN 
              f.println(s, s.@sum_score) 
          END,
  	IF print_results THEN 
              @@top_scores_heap += Vertex_Score(s, s.@sum_score) 
          END;
  IF print_results THEN
      PRINT @@top_scores_heap AS pagerank_top_nodes;
      IF display_edges THEN
          FOREACH vert IN @@top_scores_heap DO
              @@top_vertices += vert.Vertex_ID;
          END;
          Top = {@@top_vertices};
          Top = SELECT s
  	        FROM Top:s -(e_type:e)- v_type:t
              WHERE @@top_vertices.contains(t)
  	        ACCUM @@edge_set += e;
          PRINT Top;
      END;
  END;
}
"""
