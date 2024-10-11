import warnings

import pandas as pd

from config import DATA_DIR_NAME


class XlsxReader:
    """Class for reading specific xlsx files and them datas"""

    @staticmethod
    def get_input_data_from_xlsx(
        file_path=f"{DATA_DIR_NAME}/input.xlsx",
    ) -> dict[str, str]:
        file = pd.read_excel(file_path, converters={"ПРОИЗВОДИТЕЛЬ": str, "КОД": str})

        input_data = {}
        for index, row in file.iterrows():
            producer = row["ПРОИЗВОДИТЕЛЬ"]
            code = row["КОД"]

            input_data[code] = producer

        return input_data


class XlsxWriter:
    """Class for writing and changing specific xlsx files"""

    @staticmethod
    def set_rows_withtd_by_content_length(file_path: str):
        warnings.warn(
            "Call to deprecated function 'set_rows_withtd_by_content_length'.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        df = pd.read_excel(file_path)

        max_content_lengths = df.apply(lambda col: col.astype(str).apply(len).max())
        pd.set_option("display.max_colwidth", max_content_lengths.max())

        df.to_excel(file_path, index=False)
