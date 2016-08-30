# -*- coding: utf-8 -*-
import numpy as np
import xgboost as xgb
import unittest

dpath = 'demo/data/'
rng = np.random.RandomState(1994)


class TestBasic(unittest.TestCase):

    def test_basic(self):
        dtrain = xgb.DMatrix(dpath + 'agaricus.txt.train')
        dtest = xgb.DMatrix(dpath + 'agaricus.txt.test')
        param = {'max_depth': 2, 'eta': 1, 'silent': 1, 'objective': 'binary:logistic'}
        # specify validations set to watch performance
        watchlist = [(dtest, 'eval'), (dtrain, 'train')]
        num_round = 2
        bst = xgb.train(param, dtrain, num_round, watchlist)
        # this is prediction
        preds = bst.predict(dtest)
        labels = dtest.get_label()
        err = sum(1 for i in range(len(preds)) if int(preds[i] > 0.5) != labels[i]) / float(len(preds))
        # error must be smaller than 10%
        assert err < 0.1

        # save dmatrix into binary buffer
        dtest.save_binary('dtest.buffer')
        # save model
        bst.save_model('xgb.model')
        # load model and data in
        bst2 = xgb.Booster(model_file='xgb.model')
        dtest2 = xgb.DMatrix('dtest.buffer')
        preds2 = bst2.predict(dtest2)
        # assert they are the same
        assert np.sum(np.abs(preds2 - preds)) == 0

    def test_record_results(self):
        dtrain = xgb.DMatrix(dpath + 'agaricus.txt.train')
        dtest = xgb.DMatrix(dpath + 'agaricus.txt.test')
        param = {'max_depth': 2, 'eta': 1, 'silent': 1, 'objective': 'binary:logistic'}
        # specify validations set to watch performance
        watchlist = [(dtest, 'eval'), (dtrain, 'train')]
        num_round = 2
        result = {}
        res2 = {}
        xgb.train(param, dtrain, num_round, watchlist,
                  callbacks=[xgb.callback.record_evaluation(result)])
        xgb.train(param, dtrain, num_round, watchlist,
                  evals_result=res2)
        assert result['train']['error'][0] < 0.1
        assert res2 == result

    def test_multiclass(self):
        dtrain = xgb.DMatrix(dpath + 'agaricus.txt.train')
        dtest = xgb.DMatrix(dpath + 'agaricus.txt.test')
        param = {'max_depth': 2, 'eta': 1, 'silent': 1, 'num_class': 2}
        # specify validations set to watch performance
        watchlist = [(dtest, 'eval'), (dtrain, 'train')]
        num_round = 2
        bst = xgb.train(param, dtrain, num_round, watchlist)
        # this is prediction
        preds = bst.predict(dtest)

        labels = dtest.get_label()
        err = sum(1 for i in range(len(preds)) if preds[i] != labels[i]) / float(len(preds))
        # error must be smaller than 10%
        assert err < 0.1

        # save dmatrix into binary buffer
        dtest.save_binary('dtest.buffer')
        # save model
        bst.save_model('xgb.model')
        # load model and data in
        bst2 = xgb.Booster(model_file='xgb.model')
        dtest2 = xgb.DMatrix('dtest.buffer')
        preds2 = bst2.predict(dtest2)
        # assert they are the same
        assert np.sum(np.abs(preds2 - preds)) == 0

    def test_dmatrix_init(self):
        data = np.random.randn(5, 5)

        # different length
        self.assertRaises(ValueError, xgb.DMatrix, data,
                          feature_names=list('abcdef'))
        # contains duplicates
        self.assertRaises(ValueError, xgb.DMatrix, data,
                          feature_names=['a', 'b', 'c', 'd', 'd'])
        # contains symbol
        self.assertRaises(ValueError, xgb.DMatrix, data,
                          feature_names=['a', 'b', 'c', 'd', 'e<1'])

        dm = xgb.DMatrix(data)
        dm.feature_names = list('abcde')
        assert dm.feature_names == list('abcde')

        dm.feature_types = 'q'
        assert dm.feature_types == list('qqqqq')

        dm.feature_types = list('qiqiq')
        assert dm.feature_types == list('qiqiq')

        def incorrect_type_set():
            dm.feature_types = list('abcde')

        self.assertRaises(ValueError, incorrect_type_set)

        # reset
        dm.feature_names = None
        self.assertEqual(dm.feature_names, ['f0', 'f1', 'f2', 'f3', 'f4'])
        assert dm.feature_types is None

    def test_weigth_attributes(self):
        dtrain = xgb.DMatrix(dpath + 'agaricus.txt.train')
        dtest = xgb.DMatrix(dpath + 'agaricus.txt.test')
        param = {'max_depth': 6, 'eta': 1, 'silent': 1, 'objective': 'binary:logistic'}
        # specify validations set to watch performance
        watchlist = [(dtest, 'eval'), (dtrain, 'train')]
        num_round = 20
        bst = xgb.train(param, dtrain, num_round, watchlist)
        total = bst.get_tree_number()
        before = bst.get_tree_weight(0)
        new = 128. + before
        bst.set_tree_weight(0, new)
        after = bst.get_tree_weight(0)
        self.assertEqual(after, new)
        verybad = lambda: bst.get_tree_weight(total)
        self.assertRaises(IndexError, verybad)
        bst.set_tree_weight(total - 1, 128.0)
        bst.get_tree_weight(total - 1)
        # prediction before
        before = bst.predict(dtest)
        # do some shit
        for i in range(total):
            bst.set_tree_weight(i, i)
        after = bst.predict(dtest)
        self.assertFalse(np.allclose(before, after))

        # test resetting
        for i in range(total):
            bst.set_tree_weight(i, 0)
        before = bst.predict(dtest)
        for i in range(total):
            bst.set_tree_weight(i, 1)
        for i in range(total):
            bst.set_tree_weight(i, 0)
        after = bst.predict(dtest)
        self.assertTrue(np.allclose(before, after))


            # this is prediction
        # preds = bst.predict(dtest)
        # labels = dtest.get_label()
        # err = sum(1 for i in range(len(preds)) if int(preds[i] > 0.5) != labels[i]) / float(len(preds))
        # # error must be smaller than 10%
        # assert err < 0.1
        #
        # # save dmatrix into binary buffer
        # dtest.save_binary('dtest.buffer')
        # # save model
        # bst.save_model('xgb.model')
        # # load model and data in
        # bst2 = xgb.Booster(model_file='xgb.model')
        # dtest2 = xgb.DMatrix('dtest.buffer')
        # preds2 = bst2.predict(dtest2)
        # # assert they are the same
        # assert np.sum(np.abs(preds2 - preds)) == 0

    def test_weight_change_effect(self):
        # import pickle  # NOT PICKLED!!!!! >.<
        # train, valid, test, task = pickle.load(open(dpath + 'proove.pkl', 'rb'))
        # dtrain = xgb.DMatrix(*train)
        # dtest = xgb.DMatrix(*test)
        # param = {'silent' : 1, 'objective': 'multi:softmax',
        #          'numclass': 6,
        #          'booster': 'gbtree', 'alpha': 0.1, 'lambda': 1}
        dtrain = xgb.DMatrix(dpath + 'agaricus.txt.train')
        dtest = xgb.DMatrix(dpath + 'agaricus.txt.test')
        param = {'max_depth': 2, 'eta': 1, 'silent': 1, 'objective': 'binary:logistic'}

        watchlist = [(dtest, 'eval'), (dtrain, 'train')]
        num_round = 4
        bst = xgb.train(param, dtrain, num_round, watchlist)

        assert isinstance(bst, xgb.core.Booster)

        preds = bst.predict(dtest)
        labels = dtest.get_label()

        err = sum(1 for i in range(len(preds))
                  if int(preds[i] > 0.5) != labels[i]) / float(len(preds))
        assert err < 0.1

        # ODS!!!
        bst.set_tree_weights([(i, (i + 1) * (bst.get_tree_number() - i))
                              for i in range(bst.get_tree_number())])

        # condition = lambda x: x == 1000
        # assert all(map(condition, bst.get_tree_weights(range(bst.get_tree_number()))))

        newpreds = bst.predict(dtest)

        newerr = sum(1 for i in range(len(newpreds))
                     if int(preds[i] > 0.5) != labels[i]) / float(len(newpreds))
        print(">>> Error {}".format(err))
        print(">>> New error {}".format(newerr))
        print(">>> \tOld pred\tNew pred")
        for p_old, p_new in zip(preds[:5], newpreds[:5]):
            print(">>> \t{}\t{}".format(p_old, p_new))
            self.assertTrue(p_old != p_new)

    def test_feature_names(self):
        data = np.random.randn(100, 5)
        target = np.array([0, 1] * 50)

        cases = [['Feature1', 'Feature2', 'Feature3', 'Feature4', 'Feature5'],
                 [u'要因1', u'要因2', u'要因3', u'要因4', u'要因5']]

        for features in cases:
            dm = xgb.DMatrix(data, label=target,
                             feature_names=features)
            assert dm.feature_names == features
            assert dm.num_row() == 100
            assert dm.num_col() == 5

            params = {'objective': 'multi:softprob',
                      'eval_metric': 'mlogloss',
                      'eta': 0.3,
                      'num_class': 3}

            bst = xgb.train(params, dm, num_boost_round=10)
            scores = bst.get_fscore()
            assert list(sorted(k for k in scores)) == features

            dummy = np.random.randn(5, 5)
            dm = xgb.DMatrix(dummy, feature_names=features)
            bst.predict(dm)

            # different feature name must raises error
            dm = xgb.DMatrix(dummy, feature_names=list('abcde'))
            self.assertRaises(ValueError, bst.predict, dm)

    def test_feature_importances(self):
        data = np.random.randn(100, 5)
        target = np.array([0, 1] * 50)

        features = ['Feature1', 'Feature2', 'Feature3', 'Feature4', 'Feature5']

        dm = xgb.DMatrix(data, label=target,
                         feature_names=features)
        params = {'objective': 'multi:softprob',
                  'eval_metric': 'mlogloss',
                  'eta': 0.3,
                  'num_class': 3}

        bst = xgb.train(params, dm, num_boost_round=10)

        # number of feature importances should == number of features
        scores1 = bst.get_score()
        scores2 = bst.get_score(importance_type='weight')
        scores3 = bst.get_score(importance_type='cover')
        scores4 = bst.get_score(importance_type='gain')
        assert len(scores1) == len(features)
        assert len(scores2) == len(features)
        assert len(scores3) == len(features)
        assert len(scores4) == len(features)

        # check backwards compatibility of get_fscore
        fscores = bst.get_fscore()
        assert scores1 == fscores

    def test_load_file_invalid(self):
        self.assertRaises(xgb.core.XGBoostError, xgb.Booster,
                          model_file='incorrect_path')

        self.assertRaises(xgb.core.XGBoostError, xgb.Booster,
                          model_file=u'不正なパス')

    def test_dmatrix_numpy_init(self):
        data = np.random.randn(5, 5)
        dm = xgb.DMatrix(data)
        assert dm.num_row() == 5
        assert dm.num_col() == 5

        data = np.matrix([[1, 2], [3, 4]])
        dm = xgb.DMatrix(data)
        assert dm.num_row() == 2
        assert dm.num_col() == 2

        # 0d array
        self.assertRaises(ValueError, xgb.DMatrix, np.array(1))
        # 1d array
        self.assertRaises(ValueError, xgb.DMatrix, np.array([1, 2, 3]))
        # 3d array
        data = np.random.randn(5, 5, 5)
        self.assertRaises(ValueError, xgb.DMatrix, data)
        # object dtype
        data = np.array([['a', 'b'], ['c', 'd']])
        self.assertRaises(ValueError, xgb.DMatrix, data)

    def test_cv(self):
        dm = xgb.DMatrix(dpath + 'agaricus.txt.train')
        params = {'max_depth': 2, 'eta': 1, 'silent': 1, 'objective': 'binary:logistic'}

        # return np.ndarray
        cv = xgb.cv(params, dm, num_boost_round=10, nfold=10, as_pandas=False)
        assert isinstance(cv, dict)
        assert len(cv) == (4)
