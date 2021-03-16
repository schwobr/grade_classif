# AUTOGENERATED BY NBDEV! DO NOT EDIT!

__all__ = ["index", "modules", "custom_doc_links", "git_url"]

index = {"ifnone": "00_core.ipynb",
         "is_listy": "00_core.ipynb",
         "train_normalizer": "01_train.ipynb",
         "train_classifier": "01_train.ipynb",
         "train_transformer": "01_train.ipynb",
         "train_rnn_attention": "01_train.ipynb",
         "train_reargmt": "01_train.ipynb",
         "train_FLFH": "01_train.ipynb",
         "train_discriminator": "01_train.ipynb",
         "train_cancer_detector": "01_train.ipynb",
         "train_mil_cancer_detector": "01_train.ipynb",
         "train_mil_reargmt": "01_train.ipynb",
         "train_rnn_reargmt": "01_train.ipynb",
         "predict_one_scan_one_level": "02_predict.ipynb",
         "predict_one_scan": "02_predict.ipynb",
         "predict_all": "02_predict.ipynb",
         "predict_all_majority_vote": "02_predict.ipynb",
         "get_preds": "02_predict.ipynb",
         "get_slide_heatmap_cancer_detection": "02_predict.ipynb",
         "get_folder_heatmaps_cancer_detection": "02_predict.ipynb",
         "get_slide_heatmap_binary": "02_predict.ipynb",
         "get_folder_heatmaps_binary": "02_predict.ipynb",
         "get_files": "10_data.read.ipynb",
         "get_leaf_folders": "10_data.read.ipynb",
         "get_items": "10_data.read.ipynb",
         "get_scan": "10_data.read.ipynb",
         "split": "10_data.read.ipynb",
         "create_csv": "10_data.read.ipynb",
         "ItemLoader": "11_data.loaders.ipynb",
         "ImageLoader": "11_data.loaders.ipynb",
         "MaskLoader": "11_data.loaders.ipynb",
         "CategoryLoader": "11_data.loaders.ipynb",
         "SlideLoader": "11_data.loaders.ipynb",
         "FeaturesLoader": "11_data.loaders.ipynb",
         "TestDataset": "12_data.dataset.ipynb",
         "TensorDataset": "12_data.dataset.ipynb",
         "SplitDataset": "12_data.dataset.ipynb",
         "MyDataset": "12_data.dataset.ipynb",
         "ClassDataset": "12_data.dataset.ipynb",
         "ImageClassifDataset": "12_data.dataset.ipynb",
         "FeaturesClassifDataset": "12_data.dataset.ipynb",
         "ImageSegmentDataset": "12_data.dataset.ipynb",
         "NormDataset": "12_data.dataset.ipynb",
         "MILDataset": "12_data.dataset.ipynb",
         "RNNSlideDataset": "12_data.dataset.ipynb",
         "np_to_tensor": "13_data.utils.ipynb",
         "show_img": "13_data.utils.ipynb",
         "load_batches": "13_data.utils.ipynb",
         "LabelSlideBalancedRandomSampler": "13_data.utils.ipynb",
         "DeterministicHSV": "14_data.transforms.ipynb",
         "DeterministicBrightnessContrast": "14_data.transforms.ipynb",
         "DeterministicGamma": "14_data.transforms.ipynb",
         "DeterministicRGBShift": "14_data.transforms.ipynb",
         "RGB2H": "14_data.transforms.ipynb",
         "RGB2E": "14_data.transforms.ipynb",
         "RGB2HEG": "14_data.transforms.ipynb",
         "RandomCropResizeStack": "14_data.transforms.ipynb",
         "CenterCropResizeStack": "14_data.transforms.ipynb",
         "StainAugmentor": "14_data.transforms.ipynb",
         "get_transforms1": "14_data.transforms.ipynb",
         "get_transforms2": "14_data.transforms.ipynb",
         "get_transforms3": "14_data.transforms.ipynb",
         "get_transforms4": "14_data.transforms.ipynb",
         "get_transforms5": "14_data.transforms.ipynb",
         "get_transforms10": "14_data.transforms.ipynb",
         "rgb_to_lab": "15_data.color.ipynb",
         "rgb_to_hed": "15_data.color.ipynb",
         "rgb_to_h": "15_data.color.ipynb",
         "rgb_to_e": "15_data.color.ipynb",
         "rgb_to_heg": "15_data.color.ipynb",
         "ColorConverter": "15_data.color.ipynb",
         "BaseDataModule": "16_data.modules.ipynb",
         "NormDataModule": "16_data.modules.ipynb",
         "ImageClassifDataModule": "16_data.modules.ipynb",
         "FeaturesClassifDataModule": "16_data.modules.ipynb",
         "MILDataModule": "16_data.modules.ipynb",
         "RNNAggDataModule": "16_data.modules.ipynb",
         "BaseModule": "20_models.plmodules.ipynb",
         "Normalizer": "20_models.plmodules.ipynb",
         "ClassifModule": "20_models.plmodules.ipynb",
         "ImageClassifModel": "20_models.plmodules.ipynb",
         "RNNAttention": "20_models.plmodules.ipynb",
         "get_topk_idxs": "20_models.plmodules.ipynb",
         "get_max_probs": "20_models.plmodules.ipynb",
         "MILModel": "20_models.plmodules.ipynb",
         "RNNAggregator": "20_models.plmodules.ipynb",
         "CoTeachingModel": "20_models.plmodules.ipynb",
         "WSITransformer": "20_models.plmodules.ipynb",
         "EstBN": "21_models.modules.ipynb",
         "BCNorm": "21_models.modules.ipynb",
         "group_norm": "21_models.modules.ipynb",
         "bc_norm": "21_models.modules.ipynb",
         "bn_drop_lin": "21_models.modules.ipynb",
         "ConvBnRelu": "21_models.modules.ipynb",
         "ConvBn": "21_models.modules.ipynb",
         "ConvRelu": "21_models.modules.ipynb",
         "icnr": "21_models.modules.ipynb",
         "PixelShuffleICNR": "21_models.modules.ipynb",
         "DecoderBlock": "21_models.modules.ipynb",
         "LastCross": "21_models.modules.ipynb",
         "CBR": "21_models.modules.ipynb",
         "SelfAttentionBlock": "21_models.modules.ipynb",
         "SASA": "21_models.modules.ipynb",
         "SEModule": "21_models.modules.ipynb",
         "BasicBlock": "21_models.modules.ipynb",
         "SANet": "21_models.modules.ipynb",
         "sanet18": "21_models.modules.ipynb",
         "sanet34": "21_models.modules.ipynb",
         "sanet26": "21_models.modules.ipynb",
         "sanet26d": "21_models.modules.ipynb",
         "sanet50": "21_models.modules.ipynb",
         "sanet50d": "21_models.modules.ipynb",
         "DynamicUnet": "21_models.modules.ipynb",
         "Classifier": "21_models.modules.ipynb",
         "named_leaf_modules": "22_models.utils.ipynb",
         "get_sizes": "22_models.utils.ipynb",
         "gaussian_mask": "22_models.utils.ipynb",
         "get_num_features": "22_models.utils.ipynb",
         "Hook": "23_models.hooks.ipynb",
         "Hooks": "23_models.hooks.ipynb",
         "accuracy": "24_models.metrics.ipynb",
         "fp_rate": "24_models.metrics.ipynb",
         "fn_rate": "24_models.metrics.ipynb",
         "precision": "24_models.metrics.ipynb",
         "recall": "24_models.metrics.ipynb",
         "f_beta": "24_models.metrics.ipynb",
         "f_1": "24_models.metrics.ipynb",
         "pcc": "24_models.metrics.ipynb",
         "ssim": "24_models.metrics.ipynb",
         "Accuracy": "24_models.metrics.ipynb",
         "ClassifMetrics": "24_models.metrics.ipynb",
         "reduce": "25_models.losses.ipynb",
         "focal_loss": "25_models.losses.ipynb",
         "FocalLoss": "25_models.losses.ipynb",
         "BCE": "25_models.losses.ipynb",
         "PROJECT": "80_params.defaults.ipynb",
         "CSVS": "80_params.defaults.ipynb",
         "LEVEL": "80_params.defaults.ipynb",
         "DATA": "80_params.defaults.ipynb",
         "DATA_CSV": "80_params.defaults.ipynb",
         "MODELS": "80_params.defaults.ipynb",
         "COORD_CSV": "80_params.defaults.ipynb",
         "PATCH_CLASSES": "80_params.defaults.ipynb",
         "OPEN_MODE": "80_params.defaults.ipynb",
         "SAMPLE_MODE": "80_params.defaults.ipynb",
         "MODEL": "80_params.defaults.ipynb",
         "GPUS": "80_params.defaults.ipynb",
         "SIZE": "80_params.defaults.ipynb",
         "BATCH_SIZE": "80_params.defaults.ipynb",
         "LOSS": "80_params.defaults.ipynb",
         "SCHED": "80_params.defaults.ipynb",
         "REDUCTION": "80_params.defaults.ipynb",
         "EPOCHS": "80_params.defaults.ipynb",
         "DROPOUT": "80_params.defaults.ipynb",
         "LR": "80_params.defaults.ipynb",
         "WD": "80_params.defaults.ipynb",
         "NORMALIZER": "80_params.defaults.ipynb",
         "PRED_LEVELS": "80_params.defaults.ipynb",
         "SCAN": "80_params.defaults.ipynb",
         "FILT": "80_params.defaults.ipynb",
         "TRANSFORMS": "80_params.defaults.ipynb",
         "RESUME": "80_params.defaults.ipynb",
         "TRAIN_PERCENT": "80_params.defaults.ipynb",
         "TOPK": "80_params.defaults.ipynb",
         "hparams": "81_params.parser.ipynb"}

modules = ["core.py",
           "train.py",
           "predict.py",
           "data/read.py",
           "data/loaders.py",
           "data/dataset.py",
           "data/utils.py",
           "data/transforms.py",
           "data/color.py",
           "data/modules.py",
           "models/plmodules.py",
           "models/modules.py",
           "models/utils.py",
           "models/hooks.py",
           "models/metrics.py",
           "models/losses.py",
           "params/defaults.py",
           "params/parser.py"]

doc_url = "https://schwobr.github.io/grade_classif/"

git_url = "https://github.com/schwobr/grade_classif/tree/master/"

def custom_doc_links(name): return None