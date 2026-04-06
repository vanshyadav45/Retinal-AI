from ml.datasets.dataset_loader import UnifiedRetinalDatasetBuilder


def main() -> None:
    builder = UnifiedRetinalDatasetBuilder('data/raw')
    df = builder.build_master_csv('data/metadata/master_dataset.csv')
    train_df, val_df = builder.patient_level_split(df)
    print(f'Total: {len(df)} | Train: {len(train_df)} | Val: {len(val_df)}')


if __name__ == '__main__':
    main()
