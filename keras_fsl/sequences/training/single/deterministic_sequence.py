import pandas as pd

from keras_fsl.sequences.abstract_sequence import AbstractSequence


class DeterministicSequence(AbstractSequence):
    """
    Iterate over the query dataframe deterministically
    """

    def __init__(
        self,
        annotations,
        batch_size,
        shuffle=False,
        classes=None,
        labels_in_input=False,
        to_categorical=True,
        **kwargs,
    ):
        super().__init__(annotations, batch_size, **kwargs)
        self.labels_in_input = labels_in_input
        labels = pd.Categorical(self.annotations[0].label, categories=classes)
        self.targets = labels.codes
        self.shuffle = shuffle
        if to_categorical:
            self.targets = (
                pd.get_dummies(self.targets)
                .reindex(list(range(len(labels.categories))), axis=1)
            )
        self.on_epoch_end()

    def __getitem__(self, index):
        start_index = index * self.batch_size
        end_index = (index + 1) * self.batch_size
        inputs = [pd.np.stack(
            self.preprocessings[0].augment_images(self.load_img(self.annotations[0].iloc[start_index:end_index])),
            axis=0,
        )]
        output = [self.targets[start_index:end_index]]
        if self.labels_in_input:
            inputs += [output.pop()]
        return inputs, output

    def on_epoch_end(self):
        if self.shuffle:
            indexes = pd.np.random.permutation(len(self.annotations[0]))
            self.annotations[0] = self.annotations[0].iloc[indexes]
            self.targets = self.targets[indexes]
