""""
test for python2
"""
from os.path import join
from os import chdir
#from pprint import pprint
import unittest
#Constants
HomeDir='/home/ratal/workspace/mdfreader/'
testFilesDir3=join(HomeDir, 'test')
testFilesDir4=join(HomeDir,'test/MDF4/ASAM_COMMON_MDF_V4-1-0/Base_Standard/Examples/')
testPath={}
testPath['mdf3']={ '130AND_129A432_KJTECH (3779).DAT', 'T3_121121_000_6NEDC.dat', '738L10_040410 Base Acc 30km_hr.dat', '738L10 cold nedc 05101001-1.dat', '738L10_040410 Base Acc 30km_hr.mdf','datalog4.dat', 'MDF_CANAPE.mdf'}
testPath['Simple']={'ETAS_SimpleSorted.mf4', 'Vector_MinimumFile.MF4', 'Vector_CANape.MF4', 'measure2.mf4', 'measure3.mf4', 'SA001_1Hz_5927_20150120_112828.mf4', 'SA001_10Hz_0085_20150120_112828.mf4'}
testPath['DataTypes']={}
testPath['DataTypes']['IntegerTypes']={'dSPACE_IntegerTypes.mf4','ETAS_IntegerTypes.mf4','Vector_IntegerTypes.MF4'}
testPath['DataTypes']['RealTypes']={'Vector_RealTypes.MF4', 'dSPACE_RealTypes.mf4'}
testPath['DataTypes']['StringTypes']={'Vector_FixedLengthStringSBC.mf4','Vector_FixedLengthStringUTF8.mf4','Vector_FixedLengthStringUTF16_LE.mf4','Vector_FixedLengthStringUTF16_BE.mf4'}
testPath['DataTypes']['CANopenTypes']={'Vector_CANOpenDate.mf4','Vector_CANOpenTime.mf4'}
testPath['DataTypes']['ByteArray']={'Vector_ByteArrayFixedLength.mf4'}
testPath['ChannelTypes']={}
testPath['ChannelTypes']['MasterChannels']={'Vector_DifferentMasterChannels.mf4','Vector_VirtualTimeMasterChannel.mf4','Vector_NoMasterChannel.mf4'}
testPath['ChannelTypes']['MLSD']={'Vector_MLSDStringSBC.mf4','Vector_MLSDStringUTF8.mf4','Vector_MLSDStringUTF16_LE.mf4','Vector_MLSDStringUTF16_BE.mf4'}
testPath['ChannelTypes']['Synchronization']={'Vector_SyncStreamChannel.mf4'}
testPath['ChannelTypes']['VirtualData']={'Vector_VirtualDataChannelConstantConversion.mf4','Vector_VirtualDataChannelNoConversion.mf4','Vector_VirtualDataChannelLinearConversion.mf4'}
testPath['ChannelTypes']['VLSD']={'Vector_VLSDStringSBC.mf4', 'Vector_VLSDStringUTF16_LE.mf4','Vector_VLSDStringUTF16_BE.mf4','Vector_VLSDStringUTF8.mf4'}
testPath['UnsortedData']={'Vector_Unsorted_VLSD.MF4'}
testPath['Conversion']={}
testPath['Conversion']['LinearConversion']={'dSPACE_LinearConversion.mf4','Vector_LinearConversionFactor0.mf4','Vector_LinearConversion.mf4'}
testPath['Conversion']['PartialConversion']={'Vector_PartialConversionLinearIdentityAlgebraic.mf4','Vector_StatusStringTableConversionAlgebraic.mf4','Vector_PartialConversionValueRange2TextRational.mf4'}
testPath['Conversion']['RationalConversion']={'Vector_RationalConversionIntParams.mf4','Vector_RationalConversionZeroedParams.mf4','Vector_RationalConversionRealParams.mf4'}
testPath['Conversion']['LookUpConversion']={'dSPACE_Value2TextConversion.mf4','Vector_Value2ValueConversionInterpolation.mf4','dSPACE_Value2ValueConversionInterpolation.mf4','Vector_Value2ValueConversionNoInterpolation.mf4','dSPACE_Value2ValueConversionNoInterpolation.mf4','Vector_ValueRange2TextConversion.mf4','dSPACE_ValueRange2TextConversion.mf4','Vector_ValueRange2ValueConversion.mf4','Vector_Value2TextConversion.mf4'}
testPath['Conversion']['StringConversion']={'Vector_Text2TextConversion.mf4','Vector_Text2ValueConversion.mf4'}
testPath['Conversion']['TextConversion']={'dSPACE_AlgebraicConversion.mf4','Vector_AlgebraicConversionRational.mf4','Vector_AlgebraicConversionQuadratic.mf4','Vector_AlgebraicConversionSinus.mf4'}
testPath['MetaData']={'Vector_CustomExtensions_CNcomment.mf4'}
testPath['CompressedData']={}
testPath['CompressedData']['Simple']={'Vector_SingleDZ_Deflate.mf4', 'Vector_SingleDZ_TransposeDeflate.mf4'}
testPath['CompressedData']['DataList']={'Vector_DataList_Deflate.mf4', 'Vector_DataList_TransposeDeflate.mf4'}
testPath['CompressedData']['Unsorted']={'Vector_SingleDZ_Unsorted.MF4'}
testPath['DataList']={'Vector_SD_List.MF4', 'Vector_DT_EqualLen.MF4', 'ETAS_EmptyDL.mf4', 'Vector_DL_Linked_List.MF4'}
testPath['Events']={'dSPACE_Bookmarks.mf4',  'dSPACE_CaptureBlocks.mf4', 'dSPACE_HILAPITimeout.mf4', 'dSPACE_HILAPITrigger.mf4'}
testPath['SampleReduction']={'Vector_SampleReduction.mf4'}
testPath['RecordLayout']={'Vector_NotByteAligned.mf4', 'Vector_OverlappingSignals.mf4'}
testPath['Attachments']={}
testPath['Attachments']['EmbeddedCompressed']={'Vector_EmbeddedCompressed.MF4'}
testPath['Attachments']['Embedded']={'Vector_Embedded.MF4'}
testPath['Attachments']['External']={'Vector_External.MF4'}
testPath['Arrays']={'dSPACE_MeasurementArrays.mf4','Vector_MeasurementArrays.mf4','Vector_ArrayWithFixedAxes.MF4'}
testPath['ClassificationResults']={'Porsche_2D_classification_result.mf4', 'Rainflow.mf4', '2DClassification.mf4'}
testPath['BusLogging']={'Vector_CAN_DataFrame_Sort_Bus.MF4','Vector_CAN_DataFrame_Sort_ID.MF4','Vector_CAN_DataFrame_Sort_ID_SignalDesc.MF4'}
testPath['ChannelInfo']={'Vector_AttachmentRef.mf4', 'Vector_DefaultX.mf4'}

#reload mdfreader
import timeit
chdir(HomeDir)
import mdfreader
import mdfinfo4
import mdfinfo3
import imp
imp.reload(mdfreader)
imp.reload(mdfinfo4)
imp.reload(mdfinfo3)
class readfile():
    #basic file reading
    def __init__(self):
        self.example=None
        self.mdfVersion=4
    def read(self, fileName):
        print('File info : '+fileName)
        yop=mdfreader.mdfinfo(fileName)
        self.assertIsInstance(yop, mdfreader.mdfinfo)
        #pprint(yop)
        tic=timeit.default_timer()
        print('Start reading file '+fileName)
        yop=mdfreader.mdf(fileName)
        toc=timeit.default_timer()
        print(fileName+' : ', (toc-tic))
        self.assertIsInstance(yop, mdfreader.mdf)
    def write(self, fileName):
        print('Writes File : '+fileName)
        yop=mdfreader.mdf(fileName)
        yop.write(fileName)
    def resample(self, fileName):
        print('Resample File : '+fileName)
        yop=mdfreader.mdf(fileName)
        yop.resample()
    def export(self, fileName):
        print('Export File : '+fileName)
        yop=mdfreader.mdf(fileName)
        print('Export to CSV : '+fileName)
        yop.exportToCSV()
        print('Export to NetCDF : '+fileName)
        yop.exportToNetCDF()
        print('Export to HDF5 : '+fileName)
        yop.exportToHDF5()
        print('Export to Matlab : '+fileName)
        yop.exportToMatlab()
        print('Export to Excel : '+fileName)
        yop.exportToXlsx()
        print('Convert to Pandas : '+fileName)
        yop.exportToPandas()
    def MergMDF(self, fileName):
        print('Merge Files : '+fileName)
        yop=mdfreader.mdf(fileName)
        yop2=mdfreader.mdf(fileName)
        yop.mergeMdf(yop2)
        yop.copy()
    def keepChannels(self, fileName):
        print('Merge Files : '+fileName)
        yop=mdfreader.mdf(fileName)
        yop.keepChannels(yop.masterChannelList[-1])
    def singleDir(self):
        if self.mdfVersion==4:
            testFilesDir=testFilesDir4
        elif self.mdfVersion==3:
            testFilesDir=testFilesDir3
        for file in testPath[self.example]:
            fileName=join(testFilesDir, self.example, file)
            self.read(fileName)
    def doubleDir(self):
        if self.mdfVersion==4:
            testFilesDir=testFilesDir4
        elif self.mdfVersion==3:
            testFilesDir=testFilesDir3
        for path in testPath[self.example]:
            for file in testPath[self.example][path]:
                fileName=join(testFilesDir, self.example, path, file)
                self.read(fileName)
    
class simple(unittest.TestCase, readfile):
    # test simple file for mdf4
    def SetUp(self):
        self.example='Simple'
        self.mdfVersion=4
    def runTest(self):
        self.SetUp()
        self.singleDir()
        
class dataTypes(unittest.TestCase, readfile):
    def SetUp(self):
        self.example='DataTypes'
        self.mdfVersion=4
    def runTest(self):
        self.SetUp()
        self.doubleDir()

class channelTypes(unittest.TestCase, readfile):
    def SetUp(self):
        self.example='ChannelTypes'
        self.mdfVersion=4
    def runTest(self):
        self.SetUp()
        self.doubleDir()

class conversion(unittest.TestCase, readfile):
    def SetUp(self):
        self.example='Conversion'
        self.mdfVersion=4
    def runTest(self):
        self.SetUp()
        self.doubleDir()
        
class metadata(unittest.TestCase, readfile):
    # test simple file for mdf4
    def SetUp(self):
        self.example='MetaData'
        self.mdfVersion=4
    def runTest(self):
        self.SetUp()
        self.singleDir()

class compressedData(unittest.TestCase, readfile):
    def SetUp(self):
        self.example='CompressedData'
        self.mdfVersion=4
    def runTest(self):
        self.SetUp()
        self.doubleDir()

class dataList(unittest.TestCase, readfile):
    # test simple file for mdf4
    def SetUp(self):
        self.example='DataList'
        self.mdfVersion=4
    def runTest(self):
        self.SetUp()
        self.singleDir()

class events(unittest.TestCase, readfile):
    # test simple file for mdf4
    def SetUp(self):
        self.example='Events'
        self.mdfVersion=4
    def runTest(self):
        self.SetUp()
        self.singleDir()

class sampleReduction(unittest.TestCase, readfile):
    
    # test simple file for mdf4
    def SetUp(self):
        self.example='SampleReduction'
        self.mdfVersion=4
    def runTest(self):
        self.SetUp()
        self.singleDir()

class Attachments(unittest.TestCase, readfile):
    def SetUp(self):
        self.example='Attachments'
        self.mdfVersion=4
    def runTest(self):
        self.SetUp()
        self.doubleDir()

class recordLayout(unittest.TestCase, readfile):
    # test simple file for mdf4
    def SetUp(self):
        self.example='RecordLayout'
        self.mdfVersion=4
    def runTest(self):
        self.SetUp()
        self.singleDir()

class Arrays(unittest.TestCase, readfile):
    # test simple file for mdf4
    def SetUp(self):
        self.example='Arrays'
        self.mdfVersion=4
    def runTest(self):
        self.SetUp()
        self.singleDir()

class Classification(unittest.TestCase, readfile):
    # test simple file for mdf4
    def SetUp(self):
        self.example='ClassificationResults'
        self.mdfVersion=4
    def runTest(self):
        self.SetUp()
        self.singleDir()
        
class BusLogging(unittest.TestCase, readfile):
    # test simple file for mdf4
    def SetUp(self):
        self.example='BusLogging'
        self.mdfVersion=4
    def runTest(self):
        self.SetUp()
        self.singleDir()

class ChannelInfo(unittest.TestCase, readfile):
    # test simple file for mdf4
    def SetUp(self):
        self.example='ChannelInfo'
        self.mdfVersion=4
    def runTest(self):
        self.SetUp()
        self.singleDir()

# test mdf3
class mdf3(unittest.TestCase, readfile):
    def SetUp(self):
        self.example='mdf3'
        self.mdfVersion=3
        self._testMethodName='runTest'
    def runTest(self):
        self.singleDir()

def mdf4():
    suite=unittest.TestSuite()
    results=unittest.TestResult()
    suite.addTest(simple())
    suite.addTest(dataTypes())
    suite.addTest(channelTypes())
    suite.addTest(conversion())
    suite.addTest(compressedData())
    suite.addTest(dataList())
    suite.addTest(metadata())
    suite.addTest(events())
    suite.addTest(sampleReduction())
    suite.addTest(Attachments())
    suite.addTest(recordLayout())
    suite.addTest(ChannelInfo())
    suite.addTest(BusLogging())
    suite.addTest(Arrays())
    suite.addTest(Classification())
    suite.run(results)
    print(results.errors)
    return results

if __name__ == '__main__':
    unittest.main()
