from datetime import timedelta
from feast import Entity, Feature, FeatureView, RedshiftSource, ValueType

def create_transaction_entity(entity_name):
    """
    Create an Entity for transactions.

    Parameters:
    - entity_name: Name of the transaction entity.

    Returns:
    - Entity: Entity object representing the transaction entity.
    """
    return Entity(name=entity_name)

def create_redshift_source(query, event_timestamp_column, created_timestamp_column):
    """
    Create a Redshift source for transaction data.

    Parameters:
    - query: SQL query to extract transaction data from Redshift.
    - event_timestamp_column: Name of the event timestamp column in the query result.
    - created_timestamp_column: Name of the created timestamp column in the query result.

    Returns:
    - RedshiftSource: RedshiftSource object for the transaction data.
    """
    return RedshiftSource(
        query=query,
        event_timestamp_column=event_timestamp_column,
        created_timestamp_column=created_timestamp_column,
    )

def create_transaction_feature_view(
    view_name, entity_name, ttl_days, features_list, batch_source
):
    """
    Create a Feature View for transaction data.

    Parameters:
    - view_name: Name of the Feature View for transaction data.
    - entity_name: Name of the entity associated with the Feature View.
    - ttl_days: Time-to-live duration for the Feature View data.
    - features_list: List of Feature objects representing transaction features.
    - batch_source: Source from which to retrieve batch data for the Feature View.

    Returns:
    - FeatureView: FeatureView object representing transaction features.
    """
    return FeatureView(
        name=view_name,
        entities=[entity_name],
        ttl=timedelta(days=ttl_days),
        features=features_list,
        batch_source=batch_source,
    )

# Define entity
transaction_entity = create_transaction_entity("transactionid")

# Define Redshift source
transaction_source_query = "SELECT * FROM spectrum.transaction_features"
transaction_source = create_redshift_source(
    query=transaction_source_query,
    event_timestamp_column="event_timestamp",
    created_timestamp_column="created_timestamp",
)

# Define features
transaction_features_list = [
    Feature(name="productcd", dtype=ValueType.STRING),
    Feature(name="transactionamt", dtype=ValueType.DOUBLE),
    Feature(name="p_emaildomain", dtype=ValueType.STRING),
    Feature(name="r_emaildomain", dtype=ValueType.STRING),
    Feature(name="card4", dtype=ValueType.STRING),
    Feature(name="m1", dtype=ValueType.STRING),
    Feature(name="m2", dtype=ValueType.STRING),
    Feature(name="m3", dtype=ValueType.STRING),
]

# Define feature view
transaction_feature_view = create_transaction_feature_view(
    view_name="transaction_features",
    entity_name="transactionid",
    ttl_days=45,
    features_list=transaction_features_list,
    batch_source=transaction_source,
)
