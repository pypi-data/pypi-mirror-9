
def _save_vertex(id, attrs) {
    /**
     * Saves a vertex
     *
     * :param id: vertex id, if null, a new vertex is created
     * :param attrs: map of parameters to set on the vertex
     */
    try {
        def v = id == null ? g.addVertex() : g.v(id)

        for (item in attrs.entrySet()) {
            if (item.value == null) {
                v.removeProperty(item.key)
            } else {
                v.setProperty(item.key, item.value)
            }
        }
        g.stopTransaction(SUCCESS)
        return g.getVertex(v.id)
    } catch (err) {
        g.stopTransaction(FAILURE)
        throw(err)
    }
}

def _delete_vertex(id) {
    /**
     * Deletes a vertex
     *
     * :param id: vertex id
     */
     try {
        g.removeVertex(g.v(id))
        g.stopTransaction(SUCCESS)
     } catch (err) {
        g.stopTransaction(FAILURE)
        throw(err)
     }
}

def _create_relationship(id, in_direction, edge_label, edge_attrs, vertex_attrs) {
    /*
     * Creates an vertex and edge from the given vertex
     *
     * :param id: vertex id, cannot be null
     * :param direction: direction of edge from original vertex
     * :param edge_label: label of the edge
     * :param edge_attrs: map of parameters to set on the edge
     * :param vertex_attrs: map of parameters to set on the vertex
     */
    try {
        def v1 = g.v(id)
        def v2 = g.addVertex()
        def e

        for (item in vertex_attrs.entrySet()) {
                v2.setProperty(item.key, item.value)
        }
        v2 = g.getVertex(v2.id)
        if(in_direction) {
            e = g.addEdge(v2, v1, edge_label)
        } else {
            e = g.addEdge(v1, v2, edge_label)
        }
        for (item in edge_attrs.entrySet()) {
            e.setProperty(item.key, item.value)
        }
        return [g.getEdge(e.id), v2)]
    } catch (err) {
        g.stopTransaction(FAILURE)
        throw(err)
    }
}

def _traversal(id, operation, labels, start, end, element_types) {
    /**
     * performs vertex/edge traversals with optional edge labels and pagination
     * :param id: vertex id to start from
     * :param operation: the traversal operation
     * :param label: the edge label to filter on
     * :param page_num: the page number to start on (pagination begins at 1)
     * :param per_page: number of objects to return per page
     * :param element_types: list of allowed element types for results
     */
    def results = g.v(id)
    def label_args = labels == null ? [] : labels
    switch (operation) {
        case "inV":
            results = results.in(*label_args)
            break
        case "outV":
            results = results.out(*label_args)
            break
        case "inE":
            results = results.inE(*label_args)
            break
        case "outE":
            results = results.outE(*label_args)
            break
        case "bothE":
            results = results.bothE(*label_args)
            break
        case "bothV":
            results = results.both(*label_args)
            break
        default:
            throw NamingException()
    }
    if (start != null && end != null) {
        results = results[start..<end]
    }
    if (element_types != null) {
        results = results.filter{it.element_type in element_types}
    }
    return results
}

def _delete_related(id, operation, labels) {
    try{
        /**
         * deletes connected vertices / edges
         */
        def results = g.v(id)
        def label_args = labels == null ? [] : labels
        def vertices = true
        switch (operation) {
            case "inV":
                results = results.in(*label_args)
                break
            case "outV":
                results = results.out(*label_args)
                break
            case "inE":
                results = results.inE(*label_args)
                vertices = false
                break
            case "outE":
                results = results.outE(*label_args)
                vertices = false
                break
            default:
                throw NamingException()
        }
        if (vertices) {
            results.each{g.removeVertex(it)}
        } else {
            results.each{g.removeEdge(it)}
        }
        g.stopTransaction(SUCCESS)
    } catch (err) {
        g.stopTransaction(FAILURE)
        raise(err)
    }
}

def _find_vertex_by_value(value_type, element_type, field, value) {
    try {
       if (value_type) {
           return g.V("element_type", element_type).filter{it[field] == value}.toList()
       } else {
           return g.V("element_type", element_type).has(field, value).toList()
       }
    } catch (err) {
        g.stopTransaction(FAILURE)
        raise(err)
    }
}
