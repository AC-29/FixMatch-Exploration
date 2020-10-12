# Data manipulation
import numpy as np
from PIL import Image
from .CTAugment import CTAugment

# Access CIFAR-10, MNIST and SVHN
import torch
from torchvision import datasets
from torchvision import transforms

# Pre-defining mean and std for the datasets to reduce computational time
CIFAR10_mean = (0.4914, 0.4822, 0.4465)
CIFAR10_std = (0.2471, 0.2435, 0.2616)
MNIST_mean = (0.1307)
MNIST_std = (0.3081)
SVHN_mean = (0.4377, 0.4438, 0.4728)
SVHN_std = (0.1980, 0.2010, 0.1970)

###### TRANSFORMATIONS ######
def tensor_normalizer(mean, std):
    # Normalizing the testing images
    return transforms.Compose([transforms.ToTensor(), transforms.Normalize(mean=mean, std=std)])

def weakly_augmentation(mean, std):
    # Perform weak transformation on labeled and unlabeled training images
    weak_transform = transforms.Compose([
                                            transforms.RandomHorizontalFlip(),
                                            transforms.RandomCrop(size=32,
                                                                padding=int(32*0.125),
                                                                padding_mode='reflect'),
                                            transforms.ToTensor(),
                                            transforms.Normalize(mean=mean, std=std)
                                        ])
    return weak_transform

def split_labeled_unlabeled(root, num_labeled, labeled_batch_size, unlabeled_batch_size, mean, std, n_classes, balanced_split=True):
    data = datasets.CIFAR10(root, train=True, download=True)

    if balanced_split:
        lsamples_per_class = num_labeled // n_classes
        labels = np.array(data.targets)
        index_labels = []
        index_unlabeled = []
        for i in range(n_classes):
            
        
        
    else:
        print("TO DO: DEFINE UNBALANCED DATA SETS")


    # Transform label data -> weak transformation
    train_labeled_data = dataTransformation(root, labeled_indeces, train = True, transform = weakly_augmentation(mean, std))
    
    # Transform unlabeled data -> weak transformationa and CTAugment
    train_unlabeled_data = dataTransformation(root, unlabeled_indeces, train = True, transform = SSLTransform(mean, std))

    return train_labeled_data, train_unlabeled_data


###### CONSTRUCT DATA OBJECTS ######
class dataTransformation(datasets.CIFAR10):
    def __init__(self, root, indeces, train=True, transform=None, target_transform=None, download=False):
        # Accessing CIFAR10 from torchvision
        super().__init__(root, train=train,transform=transform,target_transform=target_transform,download=download)
        if indeces is not None:
            self.data = self.data[indeces]
            self.targets = np.array(self.targets)[indeces]

    def __getitem__(self, index):
        img, target = self.data[index], self.targets[index]
        img = Image.fromarray(img)

        if self.transform is not None:
            img = self.transform(img)

        return img, target

###### UNLABELED DATA WEAKLY & STRONGLY AUGMENTATION ######
class SSLTransform(object):
    def __init__(self, mean, std):
        # Weakly Data Augmentation
        self.weakly = weakly_augmentation(mean, std)

        # Strongly Data Augmentation
        self.strongly = transforms.Compose([
                                            transforms.RandomHorizontalFlip(),
                                            transforms.RandomCrop(size=32, padding=int(32*0.125), padding_mode='reflect'),
                                            CTAugment(),
                                            transforms.ToTensor(),
                                            transforms.Normalize(mean=mean, std=std)
                                        ])

    def __call__(self, x):
        weakly_augment = self.weakly(x)
        strongly_augment = self.strongly(x)
        return weakly_augment, strongly_augment

###### LOADING DATA ######
def load_cifar10(root, num_labeled, labeled_batch_size, unlabeled_batch_size):
    # Import data and define labels
    raw_data = datasets.CIFAR10(root, train=True, download=True)
    labels = raw_data.targets

    # Import test data
    test_data  = datasets.CIFAR10(root, train=False, transform = tensor_normalizer(mean = CIFAR10_mean, std = CIFAR10_std), download=False)

    # split data into labeled and unlabeled
    train_labeled_data, train_unlabeled_data = split_labeled_unlabeled(
                                                                        root,
                                                                        num_labeled,
                                                                        labeled_batch_size,
                                                                        unlabeled_batch_size,
                                                                        CIFAR10_mean,
                                                                        CIFAR10_std,
                                                                        n_classes = 10
                                                                       )

    return train_labeled_data, train_unlabeled_data, test_data






