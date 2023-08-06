#!/usr/local/bin/python
'''
Created on 25 nov. 2011

@author: merciece
'''

from obitools.graph.rootedtree import nexusFormat 


figtree="""\
begin figtree;
    set appearance.backgroundColorAttribute="User Selection";
    set appearance.backgroundColour=#-1;
    set appearance.branchColorAttribute="bc";
    set appearance.branchLineWidth=2.0;
    set appearance.foregroundColour=#-16777216;
    set appearance.selectionColour=#-2144520576;
    set branchLabels.colorAttribute="User Selection";
    set branchLabels.displayAttribute="errors";
    set branchLabels.fontName="sansserif";
    set branchLabels.fontSize=10;
    set branchLabels.fontStyle=0;
    set branchLabels.isShown=true;
    set branchLabels.significantDigits=4;
    set layout.expansion=2000;
    set layout.layoutType="RECTILINEAR";
    set layout.zoom=0;
    set nodeBars.barWidth=4.0;
    set nodeLabels.colorAttribute="User Selection";
    set nodeLabels.displayAttribute="label";
    set nodeLabels.fontName="sansserif";
    set nodeLabels.fontSize=10;
    set nodeLabels.fontStyle=0;
    set nodeLabels.isShown=true;
    set nodeLabels.significantDigits=4;
    set polarLayout.alignTipLabels=false;
    set polarLayout.angularRange=0;
    set polarLayout.rootAngle=0;
    set polarLayout.rootLength=100;
    set polarLayout.showRoot=true;
    set radialLayout.spread=0.0;
    set rectilinearLayout.alignTipLabels=false;
    set rectilinearLayout.curvature=0;
    set rectilinearLayout.rootLength=100;
    set scale.offsetAge=0.0;
    set scale.rootAge=1.0;
    set scale.scaleFactor=1.0;
    set scale.scaleRoot=false;
    set scaleAxis.automaticScale=true;
    set scaleAxis.fontSize=8.0;
    set scaleAxis.isShown=false;
    set scaleAxis.lineWidth=2.0;
    set scaleAxis.majorTicks=1.0;
    set scaleAxis.origin=0.0;
    set scaleAxis.reverseAxis=false;
    set scaleAxis.showGrid=true;
    set scaleAxis.significantDigits=4;
    set scaleBar.automaticScale=true;
    set scaleBar.fontSize=10.0;
    set scaleBar.isShown=true;
    set scaleBar.lineWidth=1.0;
    set scaleBar.scaleRange=0.0;
    set scaleBar.significantDigits=4;
    set tipLabels.colorAttribute="User Selection";
    set tipLabels.displayAttribute="Names";
    set tipLabels.fontName="sansserif";
    set tipLabels.fontSize=10;
    set tipLabels.fontStyle=0;
    set tipLabels.isShown=true;
    set tipLabels.significantDigits=4;
    set trees.order=false;
    set trees.orderType="increasing";
    set trees.rooting=false;
    set trees.rootingType="User Selection";
    set trees.transform=false;
    set trees.transformType="cladogram";
end;
"""


def cartoonRankGenerator(rank):
    def cartoon(node):
        return 'rank' in node and node['rank']==rank
    
    return cartoon


def collapseBcGenerator(Bclimit):
    def collapse(node):
        return 'bc' in node and node['bc']<=Bclimit
    return collapse


def label(node):
    if 'bc' in node:
        return "(%+3.1f) %s" % (node['bc'],node['name'])
    else:
        return "      %s" % node['name']


def main(coverageTree) :
    print nexusFormat(coverageTree,
                      label=label,
                      blocks=figtree,
                      cartoon=cartoonRankGenerator('family'))
                      #collapse=collapseBcGenerator(70))
        
