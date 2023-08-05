<%
    import projex.text
    from orb import errors
    def collect_sub_expand(schema, tree):
        output = {}
        for expand_name, sub_tree in tree.items():
            # cannot expand these keywords
            if expand_name in ('ids', 'count'):
                continue
            # these keywords are expanded via their sub-tree
            elif expand_name in ('first', 'last'):
                output.update(collect_sub_expand(schema, sub_tree))
            # lookup a column, pipe, or reverseLookup
            else:
                column = schema.column(expand_name)
                if column:
                    output[('column', column)] = sub_tree
                    continue

                pipe = schema.pipe(expand_name)
                if pipe:
                    output[('pipe', pipe)] = sub_tree
                    continue

                lookup = schema.reverseLookup(expand_name)
                if lookup:
                    output[('reverseLookup', lookup)] = sub_tree
                    continue

                raise errors.ColumnNotFound(schema.name(), expand_name)
        return output
%>

% if pipe:
    <%
        source_table = pipe.sourceReferenceModel()
        join_table = pipe.pipeReferenceModel()
        source_column = join_table.schema().column(pipe.sourceColumn())
        target_column = join_table.schema().column(pipe.targetColumn())
        target_table = pipe.targetReferenceModel()
        columns = []
        colname = pipe.name()
        col_name = projex.text.underscore(colname)

        alias = col_name + '_table'
        records_alias = col_name + '_records'

        source_table_name = source_alias or source_table.schema().dbname()

        if 'ids' in tree:
            columns.append('array_agg({0}.id) AS ids'.format(records_alias))
        if 'count' in tree:
            columns.append('count({0}.*) AS count'.format(records_alias))
        if 'first' in tree:
            columns.append('(array_agg(row_to_json({0}.*)))[1] AS first'.format(records_alias)),
        if 'last' in tree:
            columns.append('(array_agg(row_to_json({0}.*)))[count({0}.*)] AS last'.format(records_alias)),
        if 'records' in tree or not columns:
            columns.append('array_agg(row_to_json({0}.*)) AS records'.format(records_alias))
    %>
    (
        SELECT row_to_json(${col_name}_row) FROM (
            SELECT ${', '.join(columns)}
            FROM (
                SELECT ${alias}.*
                % for (type, object), sub_tree in collect_sub_expand(target_table.schema(), tree).items():
                ,${SELECT_EXPAND(**{type: object, 'tree': sub_tree, 'source_alias': alias, 'GLOBALS': GLOBALS, 'IO': IO})}
                % endfor
                FROM "${target_table.schema().dbname()}" AS "${alias}"
                WHERE "${alias}".id IN (
                    SELECT DISTINCT ON (j."${target_column.fieldName()}") j."${target_column.fieldName()}"
                    FROM "${join_table.schema().dbname()}" AS j
                    WHERE j."${source_column.fieldName()}" = "${source_table_name}".id
                    ${'LIMIT 1' if pipe.unique() else ''}
                )
            ) ${records_alias}
        ) ${col_name}_row
    ) AS "${colname}"

% elif reverseLookup:
    <%
        source_schema = reverseLookup.schema()
        source_column = reverseLookup
        ref_schema = reverseLookup.referenceModel().schema()
        ref_table_name = source_alias or ref_schema.dbname()

        colname = reverseLookup.reversedName()
        col_name = projex.text.underscore(colname)

        alias = col_name + '_table'
        records_alias = col_name + '_records'

        columns = []
        if 'ids' in tree:
            columns.append('array_agg({0}.id) AS ids'.format(records_alias))
        if 'count' in tree:
            columns.append('count({0}.*) AS count'.format(records_alias))
        if 'first' in tree:
            columns.append('(array_agg(row_to_json({0}.*)))[1] AS first'.format(records_alias)),
        if 'last' in tree:
            columns.append('(array_agg(row_to_json({0}.*)))[count({0}.*)] AS last'.format(records_alias)),
        if 'records' in tree or not columns:
            columns.append('array_agg(row_to_json({0}.*)) AS records'.format(records_alias))

    %>
    (
        SELECT row_to_json(${col_name}_row) FROM (
            SELECT ${', '.join(columns)}
            FROM (
                SELECT ${alias}.*
                % for (type, object), sub_tree in collect_sub_expand(source_schema, tree).items():
                ,${SELECT_EXPAND(**{type: object, 'tree': sub_tree, 'source_alias': alias, 'GLOBALS': GLOBALS, 'IO': IO})}
                % endfor
                FROM "${source_schema.dbname()}" AS "${alias}"
                WHERE "${alias}"."${source_column.fieldName()}" = "${ref_table_name}".id
                ${'LIMIT 1' if source_column.unique() else ''}
            ) ${records_alias}
        ) ${col_name}_row
    ) AS "${colname}"

% elif column:
    <%
        reference = column.referenceModel()
        ref_table_name = source_alias or column.schema().dbname()
        colname = column.name()
        col_name = projex.text.underscore(colname)
        alias = projex.text.underscore(column.name()) + '_table'
    %>
    (
        SELECT row_to_json(${col_name}_row) FROM (
            SELECT "${alias}".*
            % for (type, object), sub_tree in collect_sub_expand(reference.schema(), tree).items():
            ,${SELECT_EXPAND(**{type: object, 'tree': sub_tree, 'source_alias': alias, 'GLOBALS': GLOBALS, 'IO': IO})}
            % endfor
            FROM "${reference.schema().dbname()}" AS "${alias}"
            WHERE "${alias}".id = "${ref_table_name}"."${column.fieldName()}"
        ) ${col_name}_row
    ) AS "${colname}"
% endif