WCC_QUERY = """
CREATE OR REPLACE DISTRIBUTED QUERY tg_wcc (SET<STRING> v_type_set, SET<STRING> e_type_set, INT print_limit = 100,
  BOOL print_results = TRUE, STRING result_attribute = "", STRING file_path = "") SYNTAX V1 {
  /*
   This query identifies the Connected Components (undirected edges). When finished, each
   vertex is assigned an INT label = its component ID number.
    v_type_set: vertex types to traverse          print_results: print JSON output
    e_type_set: edge types to traverse            result_attribute: INT attribute to store results to
    file_path: file to write CSV output to    display_edges: output edges for visualization
    print_limit: max #vertices to output (-1 = all)  
  */

  MinAccum<INT> @min_cc_id = 0;       //each vertex's tentative component id
  MapAccum<INT, INT> @@comp_sizes_map;
  MapAccum<INT, ListAccum<INT>> @@comp_group_by_size_map;
  FILE f(file_path); 

  Start = {v_type_set};

  # Initialize: Label each vertex with its own internal ID
  S = SELECT x 
      FROM Start:x
      POST-ACCUM x.@min_cc_id = getvid(x);

  # Propagate smaller internal IDs until no more ID changes can be Done
  WHILE (S.size()>0) DO
      S = SELECT t
          FROM S:s -(e_type_set:e)- v_type_set:t
  	ACCUM t.@min_cc_id += s.@min_cc_id // If s has smaller id than t, copy the id to t
  	HAVING t.@min_cc_id != t.@min_cc_id';
  END;
  IF file_path != "" THEN
      f.println("Vertex_ID","Component_ID");
  END;

  Start = {v_type_set};
  Start = SELECT s 
          FROM Start:s
  	POST-ACCUM 
  	    IF result_attribute != "" THEN 
  	        s.setAttr(result_attribute, s.@min_cc_id) 
  	    END,
  	    IF print_results THEN 
  	        @@comp_sizes_map += (s.@min_cc_id -> 1) 
  	    END,
  	    IF file_path != "" THEN 
  	        f.println(s, s.@min_cc_id) 
  	    END;

  IF print_results THEN
      IF print_limit >= 0 THEN
          Start = SELECT s 
                  FROM Start:s 
                  LIMIT print_limit;
      END;
      FOREACH (compId,size) IN @@comp_sizes_map DO
          @@comp_group_by_size_map += (size -> compId);
      END;
      PRINT @@comp_group_by_size_map.size() AS number_of_connected_components;
  END;
}
"""
