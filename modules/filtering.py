def filtering(case_id, categorical_filter, categorical, numerical_filter_name, from1, to1, measurement_filter):

    # case_id filter
    if case_id != None:
        case_id_all = "$$" + "$$,$$".join(case_id) + "$$"
        case_id_filter = """ SELECT "Name_ID" FROM patient where "Case_ID" in ({0}) """.format(case_id_all)

    # categorical_filter
    measurement_filteru = "$$" + "$$,$$".join(measurement_filter) + "$$"
    category_filter0 = ""
    numerical_filter0 = ""
    category_filter_where = ""
    numerical_filter_where = ""

    for i in range(len(categorical)):
        cat = categorical_filter[i]
        cat = "$$"+cat[(cat.find(' is ') + 4):].replace(",", "$$,$$")+"$$"
        category_m = categorical[i].replace(" ", "_")
        category_m0 = categorical[i - 1].replace(" ", "_")

        if i == 0:
            cat_filter = """SELECT {0}."Name_ID" FROM examination_categorical AS {0}   """.format(category_m)

            cat_filter_where = """WHERE {0}."Key"=$${1}$$ AND {0}."Value" IN ({2}) AND {0}.measurement IN ({3}) """\
                .format(category_m, categorical[i], cat, measurement_filteru)

        else:
            cat_filter = """ INNER JOIN examination_categorical AS {0} ON {1}."Name_ID" = {0}."Name_ID" """\
                .format(category_m, category_m0)

            cat_filter_where = """  AND {3}."Key"=$${0}$$ AND {3}."Value" IN ({1}) AND {3}.measurement IN ({2}) """\
                .format(categorical[i], cat,measurement_filteru, category_m)

        case_cat = """ WHEN "Key"=$${0}$$ and "Value" IN ({1}) AND measurement IN ({2}) THEN "Name_ID" """\
            .format(categorical[i], cat, measurement_filteru)

        category_filter0 = category_filter0 + cat_filter
        category_filter_where = category_filter_where + cat_filter_where
    category_filter = category_filter0 + category_filter_where

    case_cat_final = """ SELECT "Name_ID",count("Name_ID")
                         FROM (SELECT CASE {0} END AS "Name_ID" FROM examination_categorical) f 
                         GROUP BY "Name_ID" 
                         HAVING count("Name_ID") = {1} """.format(case_cat, len(categorical))



    """ SELECT "Name_ID1" from (SELECT CASE WHEN "Key"=$$Diabetes$$ and "Value"[1] IN ('no') AND measurement 
    IN ('1') THEN "Name_ID" END AS "Name_ID1",CASE WHEN "Key"=$$NYHA$$ and "Value"[1] IN ('I','II') 
    AND measurement IN ('1') THEN "Name_ID" END AS "Name_ID2" FROM examination_categorical 
    where examination_categorical is not null) f group by "Name_ID1" """

    for i in range(len(from1)):
        numeric_m = numerical_filter_name[i].replace(" ", "_")
        numeric_m0 = numerical_filter_name[i - 1].replace(" ", "_")
        if i == 0:
            num_filter = """SELECT {0}."Name_ID" FROM examination_numerical as {0}   """.format(numeric_m)

            num_filter_where = """WHERE {0}."Key"=$${1}$$ AND {0}."Value" BETWEEN $${2}$$ AND $${3}$$ 
                                    AND {0}.measurement IN ({4}) """.format(numeric_m, numerical_filter_name[i],
                                                                            from1[i], to1[i], measurement_filteru)

        else:
            num_filter = """ INNER JOIN examination_numerical as {0} 
                             ON {1}."Name_ID" = {0}."Name_ID"  """.format(numeric_m, numeric_m0)

            num_filter_where = """ AND {4}."Key"=$${0}$$ 
                                   AND {4}."Value" BETWEEN $${1}$$ AND $${2}$$ 
                                   AND {4}.measurement IN ({3}) """.format(numerical_filter_name[i], from1[i], to1[i],
                                                                           measurement_filteru,numeric_m)
        case_num = """ WHEN "Key"=$${0}$$ and "Value" BETWEEN $${1}$$ AND $${2}$$ AND measurement IN ({2}) 
                       THEN "Name_ID" """.format(numerical_filter_name[i], from1[i], to1[i], measurement_filteru)

        numerical_filter0 = numerical_filter0 + num_filter
        numerical_filter_where = numerical_filter_where + num_filter_where
    numerical_filter = numerical_filter0 + numerical_filter_where

    case_num_final = """ SELECT "Name_ID",count("Name_ID")
                         FROM (SELECT CASE {0} END AS "Name_ID" FROM examination_categorical) f 
                         GROUP BY "Name_ID" 
                         HAVING count("Name_ID") = {1} """.format(case_num, len(from1))

    print(case_num_final)
    print(numerical_filter)

    # join filters
    if categorical_filter and case_id and numerical_filter_name:
        sql = """select a."Name_ID" from ({0}) AS a inner join ({1}) AS b on a."Name_ID" = b."Name_ID" inner join ({2}) AS c
        on b."Name_ID" = c."Name_ID" """.format(case_id_filter, category_filter, numerical_filter)
    elif not case_id and categorical_filter and numerical_filter_name:
        sql = """select a."Name_ID" from ({0}) AS a inner join ({1}) AS b on a."Name_ID" = b."Name_ID" """.format(
            category_filter, numerical_filter )
    elif case_id and not categorical_filter and numerical_filter_name:
        sql = """select a."Name_ID" from ({0}) AS a inner join ({1}) AS b on a."Name_ID" = b."Name_ID" """.format(
            case_id_filter, numerical_filter)
    elif case_id and categorical_filter and not numerical_filter_name:
        sql = """select a."Name_ID" from ({0}) AS a inner join ({1}) AS b on a."Name_ID" = b."Name_ID" """.format(
            case_id_filter, category_filter)
    elif not case_id and not categorical_filter and numerical_filter_name:
        sql = numerical_filter
    elif not case_id and not numerical_filter_name and categorical_filter:
        sql = category_filter
    elif case_id and not categorical_filter and not numerical_filter_name:
        sql = case_id_filter

    return sql