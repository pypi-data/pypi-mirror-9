def get_available_models():
    """
    @return a mock result that permits building, but not running, a workflow
    """
    class MockModel(object):
        def __init__(self):
            self.optimization_params = ['tau_i', 'chisq', 'k_trans', 'v_e', 'chisq']
    
    mock_mdl = MockModel()
    
    return [{'fxr.model': mock_mdl}, None, None]
