import pandas as pd
from sklearn.exceptions import NotFittedError
from sklearn.utils.validation import check_is_fitted
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBClassifier
from feast import FeatureStore
from pathlib import Path
import joblib


class FraudClassifierModel:
    # Define categorical features and target
    categorical_features = [
        "productcd",
        "p_emaildomain",
        "r_emaildomain",
        "card4",
        "m1",
        "m2",
        "m3",
    ]
    target = "isfraud"
    model_filename = "fraud_model.joblib"
    encoder_filename = "encoder.joblib"

    def __init__(self, feature_repo_path):
        """
        Initialize the FraudClassifierModel.

        Parameters:
        - feature_repo_path: Path to the feature repository.

        Initializes the Feature Store, loads or creates the model, and the encoder.
        """
        self.fs = FeatureStore(repo_path=feature_repo_path)
        self.classifier = self._load_or_create_model()
        self.encoder = self._load_or_create_encoder()

    def _load_or_create_model(self):
        """
        Load or create the XGBoost classifier model.

        Loads the saved model if exists, otherwise creates a new XGBoost classifier.

        Returns:
        - XGBClassifier: XGBoost classifier model.
        """
        if Path(self.model_filename).exists():
            return joblib.load(self.model_filename)
        return XGBClassifier()

    def _load_or_create_encoder(self):
        """
        Load or create the OneHotEncoder for categorical features.

        Loads the saved encoder if exists, otherwise creates a new OneHotEncoder.

        Returns:
        - OneHotEncoder: OneHotEncoder for categorical features.
        """
        if Path(self.encoder_filename).exists():
            return joblib.load(self.encoder_filename)
        return OneHotEncoder()

    def train(self, transactions):
        """
        Train the fraud classifier model.

        Parameters:
        - transactions: DataFrame containing transaction data.

        Trains the XGBoost classifier using transactional features and saves the model.
        """
        train_X, train_Y = self._get_training_features(transactions)
        self.classifier.fit(train_X, train_Y)
        joblib.dump(self.classifier, self.model_filename)

    def _get_training_features(self, transactions):
        """
        Extract training features for the classifier.

        Parameters:
        - transactions: DataFrame containing transaction data.

        Returns:
        - train_X: DataFrame of training features.
        - train_Y: Series of target labels.
        """
        training_df = self.fs.get_historical_features(
            entity_df=transactions[["transactionid", "event_timestamp", self.target]],
            features=self.categorical_features + ["transaction_features:transactionamt"],
        ).to_df()

        self._fit_ohe_encoder(training_df)
        train_X = self._apply_ohe_encoding(training_df)
        train_Y = training_df[self.target]
        return train_X, train_Y

    def _fit_ohe_encoder(self, requests):
        """
        Fit OneHotEncoder to categorical features.

        Parameters:
        - requests: DataFrame containing transactional features.

        Fits the OneHotEncoder to categorical features and saves the encoder.
        """
        self.encoder.fit(requests[self.categorical_features])
        joblib.dump(self.encoder, self.encoder_filename)

    def _apply_ohe_encoding(self, requests):
        """
        Apply OneHotEncoding to categorical features.

        Parameters:
        - requests: DataFrame containing transactional features.

        Returns:
        - encoded_df: DataFrame with OneHotEncoded features.
        """
        encoded = self.encoder.transform(requests[self.categorical_features])
        encoded_df = pd.DataFrame(encoded.toarray(), columns=self.encoder.get_feature_names_out())
        encoded_df["transactionamt"] = requests[["transaction_features:transactionamt"]].to_numpy()
        return encoded_df

    def predict(self, request):
        """
        Make predictions using the trained classifier.

        Parameters:
        - request: Dictionary containing transaction data.

        Returns:
        - prediction: Predicted label for the transaction.
        """
        feature_vector = self._get_online_features_from_feast(request)
        features_df = self._prepare_features(request, feature_vector)
        prediction = self._make_prediction(features_df)
        return prediction

    def _get_online_features_from_feast(self, request):
        """
        Retrieve online features using Feast.

        Parameters:
        - request: Dictionary containing transaction data.

        Returns:
        - online_features: Dictionary of online features.
        """
        transaction_id = request["transactionid"][0]
        online_features = self.fs.get_online_features(
            entity_rows=[{"transactionid": transaction_id}],
            features=self.categorical_features + ["transaction_features:transactionamt"],
        ).to_dict()
        return online_features

    def _prepare_features(self, request, feature_vector):
        """
        Prepare features for prediction.

        Parameters:
        - request: Dictionary containing transaction data.
        - feature_vector: Dictionary of feature vectors.

        Returns:
        - features_df: DataFrame of prepared features.
        """
        features = pd.DataFrame.from_dict({**request, **feature_vector})
        features_encoded = self._apply_ohe_encoding(features)
        return self._sort_columns(features_encoded)

    def _sort_columns(self, df):
        """
        Sort columns in DataFrame.

        Parameters:
        - df: DataFrame to be sorted.

        Returns:
        - df_sorted: Sorted DataFrame.
        """
        return df.reindex(sorted(df.columns), axis=1)

    def _make_prediction(self, features_df):
        """
        Make predictions using the trained classifier.

        Parameters:
        - features_df: DataFrame containing prepared features.

        Returns:
        - prediction: Predicted label for the transaction.
        """
        return self.classifier.predict(features_df)

    def is_model_trained(self):
        """
        Check if the model is trained.

        Returns:
        - bool: True if the model is trained, False otherwise.
        """
        try:
            check_is_fitted(self.classifier, "xgboost_")
        except NotFittedError:
            return False
        return True
