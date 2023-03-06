from mindspore import load_checkpoint, load_param_into_net
import os
# from model param to ckpt parm
#extra_map = {'cls_token':'cls', 'classifier.weight':'dense.weight', 'classifier.bias':'dense.bias'}
extra_map_b16_224 = {'cls_token':'cls', 'classifier.weight':'dense.weight', 'classifier.bias':'dense.bias'}
extra_map_b16_384 = {'cls_token':'cls', 'classifier.weight':'head.dense.weight', 'classifier.bias':'head.dense.bias'}
extra_maps = {'vit_b_16_224': extra_map_b16_224, 'vit_b_16_384':extra_map_b16_384}

def transfer(model, ckpt_path='vit_b_16_224.ckpt', save=True):
    param_dict = load_checkpoint(ckpt_path)
    if model_name in extra_maps:
        extra_map = extra_maps[model_name]
    else:
        extra_map = extra_map_b16_384

    print('mapping')
    ckpt_diff = False
    for param in model.get_parameters():
        if param.name not in param_dict:
            ckpt_diff = True
            #print(param.name)
            if 'backbone.' in  param.name:
                #print(param)
                ckpt_param_name = param.name.replace('backbone.', '')
                #if ckpt_param_name in param_dict:
                #print(param_dict.keys())
                if ckpt_param_name in param_dict:
                    param_dict[param.name] = param_dict.pop(ckpt_param_name)
                    #print(ckpt_param_name)
                else:
                    param_dict[param.name] = param_dict.pop(extra_map[ckpt_param_name])
            elif 'head.' in  param.name:
                ckpt_param_name = param.name.replace('head.', '')
                if ckpt_param_name in param_dict:
                    param_dict[param.name] = param_dict.pop(ckpt_param_name)
                    #print(ckpt_param_name)
                else:
                    #print(param_dict)
                    param_dict[param.name] = param_dict.pop(extra_map[ckpt_param_name])
    print('Checkpoint diff?: ', ckpt_diff)
    convert_weight = save
    if ckpt_diff and convert_weight:
        from mindspore import save_checkpoint
        load_param_into_net(model, param_dict)
        save_checkpoint(model, ckpt_path.replace('.ckpt', '_converted.ckpt'))
        print('new model ckpt saved')

if __name__=='__main__':
    import mindcv
    #model_name = 'vit_b_16_224'
    #model_name = 'vit_b_16_384'
    #model_name = 'vit_l_16_384'
    #model_name = 'vit_b_32_384'
    #model_name = 'vit_b_32_224'
    #model_name = 'vit_l_16_224'
    model_name = 'vit_l_32_224'
    model = mindcv.create_model(model_name, pretrained=True)
    transfer(model, model_name + '.ckpt')
    model = mindcv.create_model(model_name, checkpoint_path=model_name + '_converted.ckpt')
