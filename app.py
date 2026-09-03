import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# PAGE CONFIG

st.set_page_config(
    page_title="Brickview Real Estate",
    page_icon="🏠",
    layout="wide"
)


# DATABASE

conn = sqlite3.connect(
    "brickview_realestate.db",
    check_same_thread=False
)


def run_query(query, params=()):
    try:
        return pd.read_sql(query, conn, params=params)
    except Exception as e:
        st.error(f"SQL Error: {e}")
        return pd.DataFrame()


# HEADER

st.title("🏠 Brickview Real Estate")

st.write(
    "Real Estate Analysis using Python, SQL and Streamlit"
)

st.divider()


# NAVIGATION

st.sidebar.title("🏠 Brickview Real Estate")
st.sidebar.write(
    "Real Estate Intelligence"
)

page = st.sidebar.radio(
    "Navigations",
    [
        "Introduction",
        "Filters & Explorer",
        "Visualization",
        "CRUD Operations",
        "SQL Queries"
    ],
)


# Introduction

if page == "Introduction":

    st.header("📋 Introduction")

    st.write("""
    Brickview Real Estate is a comprehensive intelligence
    platform for property listings, sales analytics,
    agent performance and buyer insights.
    """)

    c1, c2, c3, c4, c5 = st.columns(5)

    listings = run_query(
        "SELECT COUNT(*) AS n FROM listings"
    ).iloc[0]["n"]

    sales = run_query(
        "SELECT COUNT(*) AS n FROM sales"
    ).iloc[0]["n"]

    buyers = run_query(
        "SELECT COUNT(*) AS n FROM buyers"
    ).iloc[0]["n"]

    agents = run_query(
        "SELECT COUNT(*) AS n FROM agents"
    ).iloc[0]["n"]
    
    average_price = run_query(
        "SELECT AVG(Price) AS n FROM listings"
    ).iloc[0]["n"]

    c1.metric("🏠 Listings", int(listings))
    c2.metric("💰 Sales", int(sales))
    c3.metric("👥 Buyers", int(buyers))
    c4.metric("👨‍💼 Agents", int(agents))
    c5.metric("💰 Average Sales Price", f"${average_price:,.0f}")

    st.divider()

    st.subheader("About Brickview")

    st.write("""
    This platform uses SQL and Python to analyze real estate
    listings, pricing, sales performance, buyer behavior and
    agent performance.
    """)

 
# FILTERS & EXPLORER

elif page == "Filters & Explorer":

    st.header("🔎 Filters & Explorer")
  
    # GET FILTER OPTIONS    

    cities = run_query("""
        SELECT DISTINCT City
        FROM listings
        WHERE City IS NOT NULL
        ORDER BY City
    """)["City"].tolist()


    property_types = run_query("""
        SELECT DISTINCT Property_Type
        FROM listings
        WHERE Property_Type IS NOT NULL
        ORDER BY Property_Type
    """)["Property_Type"].tolist()


    agent_ids = run_query("""
        SELECT DISTINCT Agent_ID
        FROM listings
        WHERE Agent_ID IS NOT NULL
        ORDER BY Agent_ID
    """)["Agent_ID"].tolist()


    max_price = run_query("""
        SELECT MAX(CAST(Price AS REAL)) AS max_price
        FROM listings
        WHERE Price IS NOT NULL
    """).iloc[0]["max_price"]

    max_price = float(max_price) if max_price is not None else 1000000
    max_price = int(max_price)


    # FILTER ROW 1    

    c1, c2, c3 = st.columns(3)


    with c1:

        selected_city = st.multiselect(
            "City",
            cities
        )


    with c2:

        selected_price = st.slider(
            "Maximum Price",
            min_value=0,
            max_value=max_price,
            value=max_price,
            step=10000
        )


    with c3:

        selected_agent = st.selectbox(
            "Agent",
            ["All"] + agent_ids
        )

    
    # FILTER ROW 2
    
    c1, c2, c3 = st.columns(3)


    with c1:

        selected_type = st.selectbox(
            "Property Type",
            ["All"] + property_types
        )


    with c2:

        listed_from = st.date_input(
            "Listed From"
        )


    with c3:

        listed_to = st.date_input(
            "Listed To"
        )

    
    # SQL QUERY    

    query = """
        SELECT
            Listing_id,
            City,
            Property_Type,
            Price,
            Sqft,
            Date_Listed,
            Agent_ID
        FROM listings
        WHERE Price <= ?
    """

    params = [selected_price]

    # CITY FILTER    

    if selected_city:

        placeholders = ",".join(
            ["?"] * len(selected_city)
        )

        query += f"""
            AND City IN ({placeholders})
        """

        params.extend(selected_city)


    # AGENT FILTER    

    if selected_agent != "All":

        query += """
            AND Agent_ID = ?
        """

        params.append(selected_agent)


    # PROPERTY TYPE FILTER

    if selected_type != "All":

        query += """
            AND Property_Type = ?
        """

        params.append(selected_type)

    
    # DATE FILTER    

    query += """
        AND Date_Listed BETWEEN ? AND ?
    """

    params.append(str(listed_from))
    params.append(str(listed_to))


    # ORDER    

    query += """
        ORDER BY Price DESC
    """
   
    # RUN QUERY    

    result = run_query(
        query,
        params
    )

    
    # RESULT   

    st.divider()

    st.subheader("🏠 Filtered Properties")


    st.metric(
        "Properties Found",
        len(result)
    )


    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )

# VISUALIZATION

elif page == "Visualization":

    st.header("📊 Real Estate Visualization")


    # MAP + BAR CHART

    c1, c2 = st.columns(2)

    # MAP CHART

    with c1:
        st.subheader("🗺️ Property Listings Map")

        map_data = run_query("""
            SELECT
                Listing_id,
                City,
                Property_Type,
                Price,
                Sqft,
                Latitude,
                Longitude
            FROM listings
            WHERE Latitude IS NOT NULL
            AND Longitude IS NOT NULL
        """)

        if not map_data.empty:

            map_data["Latitude"] = pd.to_numeric(map_data["Latitude"], errors="coerce")
            map_data["Longitude"] = pd.to_numeric(map_data["Longitude"], errors="coerce")
            map_data = map_data.dropna(subset=["Latitude", "Longitude"])

            fig = px.scatter_map(
                map_data,
                lat="Latitude",
                lon="Longitude",
                hover_name="Listing_id",
                hover_data={
                    "City": True,
                    "Property_Type": True,
                    "Price": True,
                    "Sqft": True,
                    "Latitude": False,
                    "Longitude": False
                },
                zoom=6,
                height=350
            )

            fig.update_layout(
                mapbox_style="open-street-map",
                margin=dict(
                    l=0,
                    r=0,
                    t=0,
                    b=0
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.warning("No property location data available.")

    # BAR CHART

    with c2:

        st.subheader("📊 Average Price by City")

        city_price = run_query("""
            SELECT
                City,
                AVG(Price) AS Average_Price
            FROM listings
            GROUP BY City
            ORDER BY Average_Price DESC
        """)

        if not city_price.empty:

            fig = px.bar(
                city_price,
                x="City",
                y="Average_Price",
                text_auto=".2s",
                hover_data={
                    "Average_Price": ":,.0f"
                },
                height=400
            )

            fig.update_layout(
                xaxis_title="City",
                yaxis_title="Average Price",
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20
                )
            )

            fig.update_traces(
                textposition="outside"
            )   

            st.plotly_chart(
                fig,
                use_container_width=True
            )


    st.divider()


    
    # PIE + LINE CHART
    

    c1, c2 = st.columns(2)


    # PIE CHART

    with c1:

        st.subheader("🥧 Property Type Distribution")

        property_distribution = run_query("""
            SELECT
                Property_Type,
                COUNT(*) AS Listings
            FROM listings
            GROUP BY Property_Type
            ORDER BY Listings DESC
        """)

        if not property_distribution.empty:

            st.plotly_chart(
                {
                    "data": [
                        {
                            "labels": property_distribution[
                                "Property_Type"
                            ],
                            "values": property_distribution[
                                "Listings"
                            ],
                            "type": "pie",
                            "hole": 0.35
                        }
                    ],
                    "layout": {
                        "height": 350,
                        "margin": {
                            "l": 10,
                            "r": 10,
                            "t": 40,
                            "b": 10
                        }
                    }
                },
                use_container_width=True
            )

 
    # MONTHLY LISTINGS + SALES
    
    with c2:

        st.subheader("📈 Monthly Listings & Sales")

        monthly = run_query("""
            SELECT
                Month,
                SUM(Listings) AS Listings,
                SUM(Sales) AS Sales
            FROM
            (
                SELECT
                    strftime(
                        '%Y-%m',
                        Date_Listed
                    ) AS Month,
                    COUNT(*) AS Listings,
                    0 AS Sales
                FROM listings
                GROUP BY Month

                UNION ALL

                SELECT
                    strftime(
                        '%Y-%m',
                        Date_Sold
                    ) AS Month,
                    0 AS Listings,
                    COUNT(*) AS Sales
                FROM sales
                GROUP BY Month
            )
            GROUP BY Month
            ORDER BY Month
        """)

        if not monthly.empty:

            monthly["Month"] = pd.to_datetime(
                monthly["Month"]
            )

            monthly = monthly.set_index("Month")

            st.line_chart(
                monthly[
                    ["Listings", "Sales"]
                ],
                height=350
            )


# CRUD OPERATIONS

elif page == "CRUD Operations":

    st.header("CRUD Operations")

    table = st.selectbox(
        "Select Table",
        [
            "Listings",
            "Property_Att",
            "Sales",
            "Buyers",
            "Agents"
        ]
    )

    operation = st.selectbox(
        "Select Operations",
        [
            "Create",
            "Read",
            "Update",
            "Delete"
        ]
    )

    st.divider()


    table_info = pd.read_sql_query(
        f"PRAGMA table_info({table})",
        conn
    )

    columns = table_info["name"].tolist()

    pk_columns = table_info[
        table_info["pk"] == 1
    ]["name"].tolist()

    pk = pk_columns[0] if pk_columns else columns[0]

    
    # CREATE
    
    if operation == "Create":

        st.subheader("Create Record")

        values = {}

        c1, c2, c3 = st.columns(3)

        for i, column in enumerate(columns):

            with [c1, c2, c3][i % 3]:

                values[column] = st.text_input(
                    column,
                    key=f"create_{table}_{column}"
                )

        if st.button("Create Record"):

            try:

                data = [
                    values[column]
                    for column in columns
                ]

                placeholders = ",".join(
                    ["?"] * len(columns)
                )

                conn.execute(
                    f"""
                    INSERT INTO {table}
                    ({",".join(columns)})
                    VALUES ({placeholders})
                    """,
                    data
                )

                conn.commit()

                st.success("Record created successfully!")

                st.rerun()

            except Exception as e:

                st.error(f"Create Error: {e}")


    # READ

    elif operation == "Read":

        st.subheader("Read Records")

        result = pd.read_sql_query(
            f"SELECT * FROM {table}",
            conn
        )

        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True
        )


    # UPDATE

    elif operation == "Update":

        st.subheader("Update Record")

        record_id = st.text_input(
            f"Enter {pk}"
        )

        update_column = st.selectbox(
            "Select Column",
            [
                column
                for column in columns
                if column != pk
            ]
        )

        new_value = st.text_input(
            "Enter New Value"
        )

        if st.button("Update Record"):

            try:

                cursor = conn.execute(
                    f"""
                    UPDATE {table}
                    SET {update_column} = ?
                    WHERE {pk} = ?
                    """,
                    (new_value, record_id)
                )

                conn.commit()

                if cursor.rowcount > 0:

                    st.success(
                        "Record updated successfully!"
                    )

                    st.rerun()

                else:

                    st.warning(
                        "⚠️ Record not found."
                    )

            except Exception as e:

                st.error(
                    f"Update Error: {e}"
                )


    # DELETE

    elif operation == "Delete":

        st.subheader("Delete Record")

        delete_id = st.text_input(
            f"Enter {pk}"
        )

        if st.button("Delete Record"):

            try:

                cursor = conn.execute(
                    f"""
                    DELETE FROM {table}
                    WHERE {pk} = ?
                    """,
                    (delete_id,)
                )

                conn.commit()

                if cursor.rowcount > 0:

                    st.success(
                        "Record deleted successfully!"
                    )

                    st.rerun()

                else:

                    st.warning(
                        "⚠️ Record not found."
                    )

            except Exception as e:

                st.error(
                    f"Delete Error: {e}"
                )


# SQL QUERIES

elif page == "SQL Queries":

    st.header("SQL Queries")

    question = st.selectbox(
        "Select Analysis",
        [
            "Average Listing Price by City",
            "Average Price per Sqft by Property Type",
            "Furnishing Status Impact on Property Prices",
            "Properties Near Metro Stations",
            "Rented vs Non-Rented Property Prices",
            "Bedrooms and Bathrooms Impact on Pricing",
            "Parking and Power Backup Impact on Sale Price",
            "Year Built Influence on Listing Price",
            "Highest Average Property Prices by City",
            "Property Distribution Across Price Buckets",
            "Average Days on Market by City",
            "Fastest Selling Property Types",
            "Properties Sold Above Listing Price",
            "Sale to List Price Ratio by City",
            "Properties More Than 90 Days",
            "Metro Distance Effect on Time on Market",
            "Monthly Sales Trend",
            "Currently Unsold Properties",
            "Top Agents by Deals Closed",
            "Top Agents by Total Sales Revenue",
            "Agents Who Close Deals Fastest",
            "Experience vs Deals Closed",
            "Agent Rating vs Closing Speed",
            "Average Commission by Agent",
            "Agents with Most Active Listings",
            "Investors vs End Users",
            "Highest Loan Uptake Rate by City",
            "Average Loan Amount by Buyer Type",
            "Most Common Payment Mode",
            "Loan-Backed Purchases Closing Time"
        ]
    )


    # QUERY 1
    if question == "Average Listing Price by City":

        query = """
            SELECT
                City,
                AVG(Price) AS Average_Listing_Price
            FROM listings
            GROUP BY City
            ORDER BY Average_Listing_Price DESC
        """

        result = run_query(query)


    # QUERY 2
    elif question == "Average Price per Sqft by Property Type":

        query = """
            SELECT
                Property_Type,
                AVG(Price / Sqft)
                    AS Average_Price_Per_Sqft
            FROM listings
            WHERE Sqft > 0
            GROUP BY Property_Type
            ORDER BY Average_Price_Per_Sqft DESC
        """

        result = run_query(query)


    # QUERY 3
    elif question == "Furnishing Status Impact on Property Prices":

        query = """
            SELECT
                pa.furnishing_status,
                AVG(l.Price) AS Average_Property_Price
            FROM property_att pa
            JOIN listings l
                ON pa.listing_id = l.Listing_id
            GROUP BY pa.furnishing_status
            ORDER BY Average_Property_Price DESC
        """

        result = run_query(query)


    # QUERY 4
    elif question == "Properties Near Metro Stations":

        query = """
            SELECT
                CASE
                    WHEN pa.metro_distance_km <= 2
                        THEN '0-2 km'
                    WHEN pa.metro_distance_km <= 5
                        THEN '2-5 km'
                    WHEN pa.metro_distance_km <= 10
                        THEN '5-10 km'
                    ELSE '10+ km'
                END AS Metro_Distance_Bucket,

                AVG(l.Price) AS Average_Property_Price

            FROM property_att pa

            JOIN listings l
                ON pa.listing_id = l.Listing_id

            GROUP BY Metro_Distance_Bucket

            ORDER BY Average_Property_Price DESC
        """

        result = run_query(query)


    # QUERY 5
    elif question == "Rented vs Non-Rented Property Prices":

        query = """
            SELECT
                pa.is_rented,
                AVG(l.Price) AS Average_Property_Price
            FROM property_att pa
            JOIN listings l
                ON pa.listing_id = l.Listing_id
            GROUP BY pa.is_rented
            ORDER BY Average_Property_Price DESC
        """

        result = run_query(query)


    # QUERY 6
    elif question == "Bedrooms and Bathrooms Impact on Pricing":

        query = """
            SELECT
                pa.bedrooms,
                pa.bathrooms,
                AVG(l.Price) AS Average_Property_Price
            FROM property_att pa
            JOIN listings l
                ON pa.listing_id = l.Listing_id
            GROUP BY
                pa.bedrooms,
                pa.bathrooms
            ORDER BY Average_Property_Price DESC
        """

        result = run_query(query)


    # QUERY 7
    elif question == "Parking and Power Backup Impact on Sale Price":

        query = """
            SELECT
                pa.parking_available,
                pa.power_backup,
                AVG(s.Sale_Price) AS Average_Sale_Price
            FROM property_att pa
            JOIN sales s
                ON pa.listing_id = s.Listing_ID
            GROUP BY
                pa.parking_available,
                pa.power_backup
            ORDER BY Average_Sale_Price DESC
        """

        result = run_query(query)


    # QUERY 8
    elif question == "Year Built Influence on Listing Price":

        query = """
            SELECT
                pa.year_built,
                AVG(l.Price) AS Average_Listing_Price
            FROM property_att pa
            JOIN listings l
                ON pa.listing_id = l.Listing_id
            GROUP BY pa.year_built
            ORDER BY pa.year_built
        """

        result = run_query(query)


    # QUERY 9
    elif question == "Highest Average Property Prices by City":

        query = """
            SELECT
                City,
                AVG(Price) AS Average_Property_Price
            FROM listings
            GROUP BY City
            ORDER BY Average_Property_Price DESC
        """

        result = run_query(query)


    # QUERY 10
    elif question == "Property Distribution Across Price Buckets":

        query = """
            SELECT
                CASE
                    WHEN Price < 500000
                        THEN 'Below 5 Lakh'
                    WHEN Price < 1000000
                        THEN '5-10 Lakh'
                    WHEN Price < 2500000
                        THEN '10-25 Lakh'
                    WHEN Price < 5000000
                        THEN '25-50 Lakh'
                    ELSE '50 Lakh+'
                END AS Price_Bucket,

                COUNT(*) AS Property_Count

            FROM listings

            GROUP BY Price_Bucket

            ORDER BY Property_Count DESC
        """

        result = run_query(query)


    # QUERY 11
    elif question == "Average Days on Market by City":

        query = """
            SELECT
                l.City,
                AVG(s.Days_on_Market)
                    AS Average_Days_on_Market
            FROM sales s
            JOIN listings l
                ON s.Listing_ID = l.Listing_id
            GROUP BY l.City
            ORDER BY Average_Days_on_Market DESC
        """

        result = run_query(query)


    # QUERY 12
    elif question == "Fastest Selling Property Types":

        query = """
            SELECT
                l.Property_Type,
                AVG(s.Days_on_Market)
                    AS Average_Days_on_Market
            FROM sales s
            JOIN listings l
                ON s.Listing_ID = l.Listing_id
            GROUP BY l.Property_Type
            ORDER BY Average_Days_on_Market ASC
        """

        result = run_query(query)


    # QUERY 13
    elif question == "Properties Sold Above Listing Price":

        query = """
            SELECT
                ROUND(
                    100.0 * SUM(
                        CASE
                            WHEN s.Sale_Price > l.Price
                            THEN 1
                            ELSE 0
                        END
                    ) / COUNT(*),
                    2
                ) AS Percentage_Sold_Above_Listing_Price

            FROM listings l

            JOIN sales s
                ON l.Listing_id = s.Listing_ID
        """

        result = run_query(query)


    # QUERY 14
    elif question == "Sale to List Price Ratio by City":

        query = """
            SELECT
                l.City,
                ROUND(
                    AVG(
                        s.Sale_Price * 1.0 / l.Price
                    ),
                    2
                ) AS Sale_to_List_Ratio

            FROM sales s

            JOIN listings l
                ON s.Listing_ID = l.Listing_id

            WHERE l.Price > 0

            GROUP BY l.City

            ORDER BY Sale_to_List_Ratio DESC
        """

        result = run_query(query)


    # QUERY 15
    elif question == "Properties More Than 90 Days":

        query = """
            SELECT
                s.Listing_ID,
                l.City,
                l.Property_Type,
                l.Price AS Listing_Price,
                s.Sale_Price,
                s.Days_on_Market

            FROM sales s

            JOIN listings l
                ON s.Listing_ID = l.Listing_id

            WHERE s.Days_on_Market > 90

            ORDER BY s.Days_on_Market DESC
        """

        result = run_query(query)


    # QUERY 16
    elif question == "Metro Distance Effect on Time on Market":

        query = """
            SELECT
                CASE
                    WHEN pa.metro_distance_km <= 2
                        THEN '0-2 km'
                    WHEN pa.metro_distance_km <= 5
                        THEN '2-5 km'
                    WHEN pa.metro_distance_km <= 10
                        THEN '5-10 km'
                    ELSE '10+ km'
                END AS Metro_Distance_Bucket,

                AVG(s.Days_on_Market)
                    AS Average_Days_on_Market

            FROM property_att pa

            JOIN sales s
                ON pa.listing_id = s.Listing_ID

            GROUP BY Metro_Distance_Bucket

            ORDER BY Average_Days_on_Market ASC
        """

        result = run_query(query)


    # QUERY 17
    elif question == "Monthly Sales Trend":

        query = """
            SELECT
                strftime('%Y-%m', Date_Sold)
                    AS Sale_Month,

                COUNT(*) AS Number_of_Sales,

                SUM(Sale_Price)
                    AS Total_Sales_Revenue

            FROM sales

            GROUP BY Sale_Month

            ORDER BY Sale_Month
        """

        result = run_query(query)


    # QUERY 18
    elif question == "Currently Unsold Properties":

        query = """
            SELECT
                l.Listing_id,
                l.City,
                l.Property_Type,
                l.Price AS Listing_Price,
                l.Sqft,
                l.Date_Listed

            FROM listings l

            LEFT JOIN sales s
                ON l.Listing_id = s.Listing_ID

            WHERE s.Listing_ID IS NULL

            ORDER BY l.Date_Listed
        """

        result = run_query(query)


    # QUERY 19
    elif question == "Top Agents by Deals Closed":

        query = """
            SELECT
                a.Agent_ID,
                a.Name,
                COUNT(s.Listing_ID)
                    AS Total_Sales_Closed

            FROM agents a

            JOIN listings l
                ON a.Agent_ID = l.Agent_ID

            JOIN sales s
                ON l.Listing_id = s.Listing_ID

            GROUP BY
                a.Agent_ID,
                a.Name

            ORDER BY Total_Sales_Closed DESC
        """

        result = run_query(query)


    # QUERY 20
    elif question == "Top Agents by Total Sales Revenue":

        query = """
            SELECT
                a.Agent_ID,
                a.Name,
                SUM(s.Sale_Price)
                    AS Total_Sales_Revenue

            FROM agents a

            JOIN listings l
                ON a.Agent_ID = l.Agent_ID

            JOIN sales s
                ON l.Listing_id = s.Listing_ID

            GROUP BY
                a.Agent_ID,
                a.Name

            ORDER BY Total_Sales_Revenue DESC
        """

        result = run_query(query)


    # QUERY 21
    elif question == "Agents Who Close Deals Fastest":

        query = """
            SELECT
                Agent_ID,
                Name,
                avg_closing_days
                    AS Average_Closing_Days

            FROM agents

            ORDER BY avg_closing_days ASC
        """

        result = run_query(query)


    # QUERY 22
    elif question == "Experience vs Deals Closed":

        query = """
            SELECT
                experience_years,
                deals_closed

            FROM agents

            ORDER BY experience_years ASC
        """

        result = run_query(query)


    # QUERY 23
    elif question == "Agent Rating vs Closing Speed":

        query = """
            SELECT
                Agent_ID,
                Name,
                rating,
                avg_closing_days
                    AS Average_Closing_Days

            FROM agents

            ORDER BY
                rating DESC,
                avg_closing_days ASC
        """

        result = run_query(query)


    # QUERY 24
    elif question == "Average Commission by Agent":

        query = """
            SELECT
                a.Agent_ID,
                a.Name,

                AVG(
                    s.Sale_Price *
                    a.commission_rate / 100.0
                ) AS Average_Commission_Earned

            FROM agents a

            JOIN listings l
                ON a.Agent_ID = l.Agent_ID

            JOIN sales s
                ON l.Listing_id = s.Listing_ID

            GROUP BY
                a.Agent_ID,
                a.Name

            ORDER BY Average_Commission_Earned DESC
        """

        result = run_query(query)


    # QUERY 25
    elif question == "Agents with Most Active Listings":

        query = """
            SELECT
                a.Agent_ID,
                a.Name,
                COUNT(l.Listing_id)
                    AS Active_Listings

            FROM agents a

            JOIN listings l
                ON a.Agent_ID = l.Agent_ID

            LEFT JOIN sales s
                ON l.Listing_id = s.Listing_ID

            WHERE s.Listing_ID IS NULL

            GROUP BY
                a.Agent_ID,
                a.Name

            ORDER BY Active_Listings DESC
        """

        result = run_query(query)


    # QUERY 26
    elif question == "Investors vs End Users":

        query = """
            SELECT
                buyer_type,
                COUNT(*) AS Buyer_Count,

                ROUND(
                    100.0 * COUNT(*) /
                    (SELECT COUNT(*) FROM buyers),
                    2
                ) AS Percentage

            FROM buyers

            GROUP BY buyer_type

            ORDER BY Percentage DESC
        """

        result = run_query(query)


    # QUERY 27
    elif question == "Highest Loan Uptake Rate by City":

        query = """
            SELECT
                l.City,

                ROUND(
                    100.0 * SUM(
                        CASE
                            WHEN b.loan_taken = 1
                            THEN 1
                            ELSE 0
                        END
                    ) / COUNT(*),
                    2
                ) AS Loan_Uptake_Rate

            FROM buyers b

            JOIN sales s
                ON b.sale_id = s.Listing_ID

            JOIN listings l
                ON s.Listing_ID = l.Listing_id

            GROUP BY l.City

            ORDER BY Loan_Uptake_Rate DESC
        """

        result = run_query(query)


    # QUERY 28
    elif question == "Average Loan Amount by Buyer Type":

        query = """
            SELECT
                buyer_type,
                AVG(loan_amount)
                    AS Average_Loan_Amount

            FROM buyers

            WHERE loan_taken = 1

            GROUP BY buyer_type

            ORDER BY Average_Loan_Amount DESC
        """

        result = run_query(query)


    # QUERY 29
    elif question == "Most Common Payment Mode":

        query = """
            SELECT
                payment_mode,
                COUNT(*) AS Usage_Count

            FROM buyers

            GROUP BY payment_mode

            ORDER BY Usage_Count DESC
        """

        result = run_query(query)


    # QUERY 30
    elif question == "Loan-Backed Purchases Closing Time":

        query = """
            SELECT
                b.loan_taken,

                AVG(s.Days_on_Market)
                    AS Average_Days_on_Market

            FROM buyers b

            JOIN sales s
                ON b.sale_id = s.Listing_ID

            GROUP BY b.loan_taken

            ORDER BY Average_Days_on_Market ASC
        """

        result = run_query(query)


    # RESULT TABLE

    st.subheader("📋 Query Result")

    if not result.empty:

        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            f"Total records: {len(result)}"
        )

    else:

        st.warning(
            "No records found."
        )


conn.close()
