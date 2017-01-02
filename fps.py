import  pygame
import  config as G
import  numpy as np

'''
=============================
FPS
=============================
'''
class FPS:

    '''
    =============================
    __init__
    =============================
    '''
    def __init__(self):
        self.font_size  = 20
        self.color      = (165, 165, 165)
        self.font       = pygame.font.SysFont('Liberation Mono', self.font_size)
        self.text       = ''
        self.sample     = []
        self.rect       = pygame.Rect(G.screen.get_rect().width-50, 5, 50, self.font_size)
        self.surface    = G.background.subsurface(self.rect)
        G.dirty_rects.append(self.rect)
    
    '''
    =============================
    update
    =============================
    '''
    def update(self, dt):
        if len(self.sample) > 10: del(self.sample[0])
        self.sample.append(dt)
        mean = np.mean(self.sample)
        if mean: self.text = str(int(1/mean))

    '''
    =============================
    draw
    =============================
    '''
    def draw(self, screen):
        screen.blit(self.surface, self.rect)
        text = self.font.render(self.text, 0, self.color)
        screen.blit(text, self.rect)
