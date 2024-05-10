"""
Basic tests for the UNetGNRes U-Net implementation.
Can the network be trained to approximate and target.
"""

from unet import UNetGNRes


def setup_function():
    import os
    """setup any state tied to the execution of the given function.
    Invoked for every test function in the module.
    """
    if not os.path.isdir('test_temp_output'):
        os.makedirs('test_temp_output')


def test_inference():
    """ should not raise an exception """
    import torch
    from model_utils import get_device
    from PIL import Image
    device = get_device()
    from torch.nn.functional import softmax
    from skimage.io import imsave
    import numpy as np
    from skimage import img_as_uint
    unet = UNetGNRes()
    unet.eval()
    unet.to(device)
    test_input = np.zeros((1, 3, 572, 572))
    test_input = torch.from_numpy(test_input)
    test_input = test_input.float().to(device)
    output = unet(test_input)
    output = output.detach().cpu()
    output = output[0] # single image.
    output = output.numpy()
    im = img_as_uint(output)
    imsave('test_temp_output/out.png', im, check_contrast=False)


def test_training():
    """ test that network can be trained,
        and can approximate a square """
    import torch
    from model_utils import get_device
    import numpy as np
    from loss import combined_loss as criterion

    # this seems to work well and is simpler, but further testing is required.
    # from torch.nn.functional import cross_entropy
    from skimage.io import imsave
    from skimage import img_as_uint

    device = get_device()
    unet = UNetGNRes()
    unet.to(device)
    optimizer = torch.optim.SGD(unet.parameters(), lr=0.01,
                                momentum=0.99, nesterov=True)

    test_input = np.zeros((1, 3, 572, 572))
    test_input[:, :, 100:-100,100:-100] = 1.0
    test_input = torch.from_numpy(test_input)
    test_input = test_input.float().to(device)
    target = (test_input[:, 0, 36:-36, 36:-36] > 0.5)
    im = img_as_uint(target.cpu().numpy())
    for step in range(300):
        optimizer.zero_grad()
        output = unet(test_input)
        loss = criterion(output, target) # all zeros output
        # print('loss', loss.item())
        loss.backward()
        optimizer.step()
        im = output.detach().cpu().numpy()[0]
        im = img_as_uint(im)
        imsave('test_temp_output/out_' + str(step).zfill(3) + '.png', im,
               check_contrast=False)
        # if loss < 1e-7: this requires model update see unetv2
        if loss < 1.1e-3:
            print('reached loss of ', loss.item(), 'after', step, 'steps')
            return # test passes. loss is low enough
    raise Exception('loss too high, loss = ' + str(loss.item()))


def test_training_with_mask():
    """ test that network can be trained,
        and can approximate a square.
        This time also using a mask of the 'defined' region """

    import torch
    from model_utils import get_device
    import numpy as np
    from torch.nn.functional import softmax, binary_cross_entropy 
    from loss import combined_loss as criterion

    # would like to experiment with switching to these but more experiments required.
    #from torch.nn.functional import cross_entropy, binary_cross_entropy
    from skimage.io import imsave
    from skimage import img_as_uint
    device = get_device()
    unet = UNetGNRes()
    unet.to(device)
    optimizer = torch.optim.SGD(unet.parameters(), lr=0.01,
                                momentum=0.99, nesterov=True)
    test_input = np.zeros((1, 3, 572, 572))
    test_input[:, :, 100:-100,100:-100] = 1.0
    test_input = torch.from_numpy(test_input)
    test_input = test_input.float().to(device)
    target = (test_input[:, 0, 36:-36, 36:-36] > 0.5)
    target = target.float().to(device)

    imsave('test_temp_output/targ.png',
           img_as_uint(target.float().cpu().numpy()),
           check_contrast=False)

    defined = np.zeros((1, 500, 500))
    defined[:, :250] = 1
    defined = torch.from_numpy(defined).float().to(device)

    target = torch.mul(target, defined)
    for step in range(30000):
        optimizer.zero_grad()
        preds = unet(test_input)

        loss = criterion(preds, target, defined)
        print('loss', loss.item())
        loss.backward()
        optimizer.step()
        im = preds.detach().cpu().numpy()[0]
        im = img_as_uint(im)
        imsave('test_temp_output/out_' + str(step).zfill(3) + '.png', im,
               check_contrast=False)
        if loss < 0.01:
            print('reached loss of ', loss.item(), 'after', step, 'steps')
            return # test passes. loss is low enough
    raise Exception('loss too high, loss = ' + str(loss.item()))
