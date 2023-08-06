# Generated from java-escape by ANTLR 4.5
# encoding: utf-8
from antlr4 import *
from io import StringIO
package = globals().get("__package__", None)
ischild = len(package)>0 if package is not None else False
if ischild:
    from .pddlListener import pddlListener
else:
    from pddlListener import pddlListener
def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\3s")
        buf.write("\u03ae\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\4\16")
        buf.write("\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22\4\23\t\23")
        buf.write("\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30\4\31")
        buf.write("\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\4\36\t\36")
        buf.write("\4\37\t\37\4 \t \4!\t!\4\"\t\"\4#\t#\4$\t$\4%\t%\4&\t")
        buf.write("&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4,\t,\4-\t-\4.\t.\4")
        buf.write("/\t/\4\60\t\60\4\61\t\61\4\62\t\62\4\63\t\63\4\64\t\64")
        buf.write("\4\65\t\65\4\66\t\66\4\67\t\67\48\t8\49\t9\4:\t:\4;\t")
        buf.write(";\4<\t<\4=\t=\4>\t>\4?\t?\4@\t@\4A\tA\4B\tB\4C\tC\4D\t")
        buf.write("D\4E\tE\4F\tF\4G\tG\4H\tH\3\2\3\2\5\2\u0093\n\2\3\3\3")
        buf.write("\3\3\3\3\3\5\3\u0099\n\3\3\3\5\3\u009c\n\3\3\3\5\3\u009f")
        buf.write("\n\3\3\3\5\3\u00a2\n\3\3\3\5\3\u00a5\n\3\3\3\5\3\u00a8")
        buf.write("\n\3\3\3\7\3\u00ab\n\3\f\3\16\3\u00ae\13\3\3\3\3\3\3\4")
        buf.write("\3\4\3\4\3\4\3\4\3\5\3\5\3\5\6\5\u00ba\n\5\r\5\16\5\u00bb")
        buf.write("\3\5\3\5\3\6\3\6\3\6\3\6\3\6\3\7\7\7\u00c6\n\7\f\7\16")
        buf.write("\7\u00c9\13\7\3\7\6\7\u00cc\n\7\r\7\16\7\u00cd\3\7\7\7")
        buf.write("\u00d1\n\7\f\7\16\7\u00d4\13\7\5\7\u00d6\n\7\3\b\6\b\u00d9")
        buf.write("\n\b\r\b\16\b\u00da\3\b\3\b\3\b\3\t\3\t\3\t\6\t\u00e3")
        buf.write("\n\t\r\t\16\t\u00e4\3\t\3\t\3\t\5\t\u00ea\n\t\3\n\3\n")
        buf.write("\3\13\3\13\3\13\3\13\3\13\3\f\6\f\u00f4\n\f\r\f\16\f\u00f5")
        buf.write("\3\f\3\f\5\f\u00fa\n\f\7\f\u00fc\n\f\f\f\16\f\u00ff\13")
        buf.write("\f\3\r\3\r\3\r\3\r\3\r\3\16\3\16\3\17\3\17\3\20\3\20\3")
        buf.write("\20\3\20\3\20\3\21\3\21\3\21\6\21\u0112\n\21\r\21\16\21")
        buf.write("\u0113\3\21\3\21\3\22\3\22\3\22\3\22\3\22\3\23\3\23\3")
        buf.write("\24\7\24\u0120\n\24\f\24\16\24\u0123\13\24\3\24\6\24\u0126")
        buf.write("\n\24\r\24\16\24\u0127\3\24\7\24\u012b\n\24\f\24\16\24")
        buf.write("\u012e\13\24\5\24\u0130\n\24\3\25\6\25\u0133\n\25\r\25")
        buf.write("\16\25\u0134\3\25\3\25\3\25\3\26\3\26\3\26\3\26\3\26\3")
        buf.write("\27\3\27\3\27\5\27\u0142\n\27\3\30\3\30\3\30\3\30\3\30")
        buf.write("\3\30\3\30\3\30\3\30\3\30\3\31\3\31\3\32\3\32\3\32\3\32")
        buf.write("\5\32\u0154\n\32\5\32\u0156\n\32\3\32\3\32\3\32\3\32\5")
        buf.write("\32\u015c\n\32\5\32\u015e\n\32\3\33\3\33\3\34\3\34\3\34")
        buf.write("\3\34\7\34\u0166\n\34\f\34\16\34\u0169\13\34\3\34\3\34")
        buf.write("\3\34\3\34\7\34\u016f\n\34\f\34\16\34\u0172\13\34\3\34")
        buf.write("\3\34\3\34\3\34\3\34\3\34\3\34\3\34\3\34\3\34\3\34\3\34")
        buf.write("\3\34\3\34\3\34\3\34\3\34\3\34\3\34\3\34\3\34\3\34\3\34")
        buf.write("\3\34\3\34\3\34\3\34\3\34\3\34\5\34\u0191\n\34\3\35\3")
        buf.write("\35\3\35\3\35\3\35\3\35\3\36\3\36\3\36\7\36\u019c\n\36")
        buf.write("\f\36\16\36\u019f\13\36\3\36\3\36\3\37\3\37\3 \3 \3 \3")
        buf.write(" \3 \3 \3 \3 \3 \3 \3!\3!\3!\3!\3!\3!\5!\u01b5\n!\3!\3")
        buf.write("!\3!\3!\5!\u01bb\n!\5!\u01bd\n!\3\"\3\"\3\"\3\"\7\"\u01c3")
        buf.write("\n\"\f\"\16\"\u01c6\13\"\3\"\3\"\3\"\3\"\3\"\3\"\3\"\3")
        buf.write("\"\3\"\5\"\u01d1\n\"\3#\3#\3#\3#\5#\u01d7\n#\3#\3#\3#")
        buf.write("\5#\u01dc\n#\3$\3$\3$\3$\3$\3$\3$\3$\3$\3$\3$\3$\5$\u01ea")
        buf.write("\n$\3%\3%\3&\3&\3\'\3\'\3\'\3\'\3\'\3\'\3(\3(\3(\3(\3")
        buf.write("(\3(\3(\3(\3(\3(\3(\3(\3(\5(\u0203\n(\3)\3)\3*\3*\3*\7")
        buf.write("*\u020a\n*\f*\16*\u020d\13*\3*\3*\3*\5*\u0212\n*\3+\3")
        buf.write("+\3+\7+\u0217\n+\f+\16+\u021a\13+\3+\3+\5+\u021e\n+\3")
        buf.write(",\3,\3,\3,\3,\3,\3,\3,\3,\3,\3,\3,\3,\3,\3,\5,\u022f\n")
        buf.write(",\3-\3-\3-\3-\3-\3-\3-\3-\3-\3-\3-\3-\5-\u023d\n-\3.\3")
        buf.write(".\3.\7.\u0242\n.\f.\16.\u0245\13.\3.\3.\5.\u0249\n.\3")
        buf.write("/\3/\3\60\3\60\3\61\3\61\3\62\3\62\3\62\6\62\u0254\n\62")
        buf.write("\r\62\16\62\u0255\3\62\3\62\3\62\3\62\3\62\5\62\u025d")
        buf.write("\n\62\3\63\3\63\3\63\3\63\3\63\3\63\3\63\3\63\3\63\3\63")
        buf.write("\3\63\3\63\5\63\u026b\n\63\3\64\3\64\3\65\3\65\5\65\u0271")
        buf.write("\n\65\3\66\3\66\3\66\7\66\u0276\n\66\f\66\16\66\u0279")
        buf.write("\13\66\3\66\3\66\3\66\3\66\3\66\3\66\3\66\3\66\3\66\3")
        buf.write("\66\3\66\3\66\3\66\3\66\3\66\3\66\3\66\3\66\3\66\3\66")
        buf.write("\3\66\3\66\5\66\u0291\n\66\3\67\3\67\3\67\3\67\3\67\3")
        buf.write("\67\3\67\3\67\3\67\3\67\3\67\3\67\3\67\3\67\3\67\3\67")
        buf.write("\3\67\3\67\5\67\u02a5\n\67\38\38\38\38\38\38\39\39\39")
        buf.write("\39\39\39\39\59\u02b4\n9\39\39\39\39\59\u02ba\n9\3:\3")
        buf.write(":\3:\3:\3:\5:\u02c1\n:\3:\5:\u02c4\n:\3:\3:\3:\5:\u02c9")
        buf.write("\n:\3:\5:\u02cc\n:\3:\3:\3;\3;\3;\3;\3;\3<\3<\3<\3<\3")
        buf.write("<\3=\3=\3=\3=\3=\3>\3>\3>\7>\u02e2\n>\f>\16>\u02e5\13")
        buf.write(">\3>\3>\3?\3?\3?\3?\3?\3?\3?\3?\3?\3?\3?\3?\3?\5?\u02f6")
        buf.write("\n?\3@\3@\3@\3@\3@\3@\5@\u02fe\n@\3A\3A\3A\7A\u0303\n")
        buf.write("A\fA\16A\u0306\13A\3A\3A\3B\3B\3B\3B\3B\3C\3C\3C\3C\3")
        buf.write("C\3D\3D\3D\7D\u0317\nD\fD\16D\u031a\13D\3D\3D\3D\3D\3")
        buf.write("D\3D\3D\3D\3D\3D\3D\3D\5D\u0328\nD\3D\3D\3D\3D\5D\u032e")
        buf.write("\nD\3E\3E\3E\3E\3E\3E\3F\3F\3G\3G\3G\3G\3G\3G\3G\3G\3")
        buf.write("G\3G\6G\u0342\nG\rG\16G\u0343\3G\3G\3G\3G\3G\3G\3G\3G")
        buf.write("\3G\3G\3G\7G\u0351\nG\fG\16G\u0354\13G\3G\3G\3G\3G\3G")
        buf.write("\3G\3G\3G\5G\u035e\nG\3H\3H\3H\7H\u0363\nH\fH\16H\u0366")
        buf.write("\13H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3")
        buf.write("H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3")
        buf.write("H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3")
        buf.write("H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\3H\5H\u03ac")
        buf.write("\nH\3H\2\2I\2\4\6\b\n\f\16\20\22\24\26\30\32\34\36 \"")
        buf.write("$&(*,.\60\62\64\668:<>@BDFHJLNPRTVXZ\\^`bdfhjlnprtvxz")
        buf.write("|~\u0080\u0082\u0084\u0086\u0088\u008a\u008c\u008e\2\n")
        buf.write("\3\2GH\3\2 !\4\2\t\t%\'\3\2(,\3\2-\61\3\2*,\3\29:\4\2")
        buf.write("%%\'\'\u03d8\2\u0092\3\2\2\2\4\u0094\3\2\2\2\6\u00b1\3")
        buf.write("\2\2\2\b\u00b6\3\2\2\2\n\u00bf\3\2\2\2\f\u00d5\3\2\2\2")
        buf.write("\16\u00d8\3\2\2\2\20\u00e9\3\2\2\2\22\u00eb\3\2\2\2\24")
        buf.write("\u00ed\3\2\2\2\26\u00fd\3\2\2\2\30\u0100\3\2\2\2\32\u0105")
        buf.write("\3\2\2\2\34\u0107\3\2\2\2\36\u0109\3\2\2\2 \u010e\3\2")
        buf.write("\2\2\"\u0117\3\2\2\2$\u011c\3\2\2\2&\u012f\3\2\2\2(\u0132")
        buf.write("\3\2\2\2*\u0139\3\2\2\2,\u0141\3\2\2\2.\u0143\3\2\2\2")
        buf.write("\60\u014d\3\2\2\2\62\u0155\3\2\2\2\64\u015f\3\2\2\2\66")
        buf.write("\u0190\3\2\2\28\u0192\3\2\2\2:\u0198\3\2\2\2<\u01a2\3")
        buf.write("\2\2\2>\u01a4\3\2\2\2@\u01bc\3\2\2\2B\u01d0\3\2\2\2D\u01db")
        buf.write("\3\2\2\2F\u01e9\3\2\2\2H\u01eb\3\2\2\2J\u01ed\3\2\2\2")
        buf.write("L\u01ef\3\2\2\2N\u0202\3\2\2\2P\u0204\3\2\2\2R\u0211\3")
        buf.write("\2\2\2T\u021d\3\2\2\2V\u022e\3\2\2\2X\u023c\3\2\2\2Z\u0248")
        buf.write("\3\2\2\2\\\u024a\3\2\2\2^\u024c\3\2\2\2`\u024e\3\2\2\2")
        buf.write("b\u025c\3\2\2\2d\u026a\3\2\2\2f\u026c\3\2\2\2h\u0270\3")
        buf.write("\2\2\2j\u0290\3\2\2\2l\u02a4\3\2\2\2n\u02a6\3\2\2\2p\u02b9")
        buf.write("\3\2\2\2r\u02bb\3\2\2\2t\u02cf\3\2\2\2v\u02d4\3\2\2\2")
        buf.write("x\u02d9\3\2\2\2z\u02de\3\2\2\2|\u02f5\3\2\2\2~\u02fd\3")
        buf.write("\2\2\2\u0080\u02ff\3\2\2\2\u0082\u0309\3\2\2\2\u0084\u030e")
        buf.write("\3\2\2\2\u0086\u032d\3\2\2\2\u0088\u032f\3\2\2\2\u008a")
        buf.write("\u0335\3\2\2\2\u008c\u035d\3\2\2\2\u008e\u03ab\3\2\2\2")
        buf.write("\u0090\u0093\5\4\3\2\u0091\u0093\5r:\2\u0092\u0090\3\2")
        buf.write("\2\2\u0092\u0091\3\2\2\2\u0093\3\3\2\2\2\u0094\u0095\7")
        buf.write("\3\2\2\u0095\u0096\7\4\2\2\u0096\u0098\5\6\4\2\u0097\u0099")
        buf.write("\5\b\5\2\u0098\u0097\3\2\2\2\u0098\u0099\3\2\2\2\u0099")
        buf.write("\u009b\3\2\2\2\u009a\u009c\5\n\6\2\u009b\u009a\3\2\2\2")
        buf.write("\u009b\u009c\3\2\2\2\u009c\u009e\3\2\2\2\u009d\u009f\5")
        buf.write("\36\20\2\u009e\u009d\3\2\2\2\u009e\u009f\3\2\2\2\u009f")
        buf.write("\u00a1\3\2\2\2\u00a0\u00a2\5 \21\2\u00a1\u00a0\3\2\2\2")
        buf.write("\u00a1\u00a2\3\2\2\2\u00a2\u00a4\3\2\2\2\u00a3\u00a5\5")
        buf.write("\24\13\2\u00a4\u00a3\3\2\2\2\u00a4\u00a5\3\2\2\2\u00a5")
        buf.write("\u00a7\3\2\2\2\u00a6\u00a8\5*\26\2\u00a7\u00a6\3\2\2\2")
        buf.write("\u00a7\u00a8\3\2\2\2\u00a8\u00ac\3\2\2\2\u00a9\u00ab\5")
        buf.write(",\27\2\u00aa\u00a9\3\2\2\2\u00ab\u00ae\3\2\2\2\u00ac\u00aa")
        buf.write("\3\2\2\2\u00ac\u00ad\3\2\2\2\u00ad\u00af\3\2\2\2\u00ae")
        buf.write("\u00ac\3\2\2\2\u00af\u00b0\7\5\2\2\u00b0\5\3\2\2\2\u00b1")
        buf.write("\u00b2\7\3\2\2\u00b2\u00b3\7\6\2\2\u00b3\u00b4\7G\2\2")
        buf.write("\u00b4\u00b5\7\5\2\2\u00b5\7\3\2\2\2\u00b6\u00b7\7\3\2")
        buf.write("\2\u00b7\u00b9\7\7\2\2\u00b8\u00ba\7F\2\2\u00b9\u00b8")
        buf.write("\3\2\2\2\u00ba\u00bb\3\2\2\2\u00bb\u00b9\3\2\2\2\u00bb")
        buf.write("\u00bc\3\2\2\2\u00bc\u00bd\3\2\2\2\u00bd\u00be\7\5\2\2")
        buf.write("\u00be\t\3\2\2\2\u00bf\u00c0\7\3\2\2\u00c0\u00c1\7\b\2")
        buf.write("\2\u00c1\u00c2\5\f\7\2\u00c2\u00c3\7\5\2\2\u00c3\13\3")
        buf.write("\2\2\2\u00c4\u00c6\7G\2\2\u00c5\u00c4\3\2\2\2\u00c6\u00c9")
        buf.write("\3\2\2\2\u00c7\u00c5\3\2\2\2\u00c7\u00c8\3\2\2\2\u00c8")
        buf.write("\u00d6\3\2\2\2\u00c9\u00c7\3\2\2\2\u00ca\u00cc\5\16\b")
        buf.write("\2\u00cb\u00ca\3\2\2\2\u00cc\u00cd\3\2\2\2\u00cd\u00cb")
        buf.write("\3\2\2\2\u00cd\u00ce\3\2\2\2\u00ce\u00d2\3\2\2\2\u00cf")
        buf.write("\u00d1\7G\2\2\u00d0\u00cf\3\2\2\2\u00d1\u00d4\3\2\2\2")
        buf.write("\u00d2\u00d0\3\2\2\2\u00d2\u00d3\3\2\2\2\u00d3\u00d6\3")
        buf.write("\2\2\2\u00d4\u00d2\3\2\2\2\u00d5\u00c7\3\2\2\2\u00d5\u00cb")
        buf.write("\3\2\2\2\u00d6\r\3\2\2\2\u00d7\u00d9\7G\2\2\u00d8\u00d7")
        buf.write("\3\2\2\2\u00d9\u00da\3\2\2\2\u00da\u00d8\3\2\2\2\u00da")
        buf.write("\u00db\3\2\2\2\u00db\u00dc\3\2\2\2\u00dc\u00dd\7\t\2\2")
        buf.write("\u00dd\u00de\5\20\t\2\u00de\17\3\2\2\2\u00df\u00e0\7\3")
        buf.write("\2\2\u00e0\u00e2\7\n\2\2\u00e1\u00e3\5\22\n\2\u00e2\u00e1")
        buf.write("\3\2\2\2\u00e3\u00e4\3\2\2\2\u00e4\u00e2\3\2\2\2\u00e4")
        buf.write("\u00e5\3\2\2\2\u00e5\u00e6\3\2\2\2\u00e6\u00e7\7\5\2\2")
        buf.write("\u00e7\u00ea\3\2\2\2\u00e8\u00ea\5\22\n\2\u00e9\u00df")
        buf.write("\3\2\2\2\u00e9\u00e8\3\2\2\2\u00ea\21\3\2\2\2\u00eb\u00ec")
        buf.write("\7G\2\2\u00ec\23\3\2\2\2\u00ed\u00ee\7\3\2\2\u00ee\u00ef")
        buf.write("\7\13\2\2\u00ef\u00f0\5\26\f\2\u00f0\u00f1\7\5\2\2\u00f1")
        buf.write("\25\3\2\2\2\u00f2\u00f4\5\30\r\2\u00f3\u00f2\3\2\2\2\u00f4")
        buf.write("\u00f5\3\2\2\2\u00f5\u00f3\3\2\2\2\u00f5\u00f6\3\2\2\2")
        buf.write("\u00f6\u00f9\3\2\2\2\u00f7\u00f8\7\t\2\2\u00f8\u00fa\5")
        buf.write("\34\17\2\u00f9\u00f7\3\2\2\2\u00f9\u00fa\3\2\2\2\u00fa")
        buf.write("\u00fc\3\2\2\2\u00fb\u00f3\3\2\2\2\u00fc\u00ff\3\2\2\2")
        buf.write("\u00fd\u00fb\3\2\2\2\u00fd\u00fe\3\2\2\2\u00fe\27\3\2")
        buf.write("\2\2\u00ff\u00fd\3\2\2\2\u0100\u0101\7\3\2\2\u0101\u0102")
        buf.write("\5\32\16\2\u0102\u0103\5&\24\2\u0103\u0104\7\5\2\2\u0104")
        buf.write("\31\3\2\2\2\u0105\u0106\7G\2\2\u0106\33\3\2\2\2\u0107")
        buf.write("\u0108\7\f\2\2\u0108\35\3\2\2\2\u0109\u010a\7\3\2\2\u010a")
        buf.write("\u010b\7\r\2\2\u010b\u010c\5\f\7\2\u010c\u010d\7\5\2\2")
        buf.write("\u010d\37\3\2\2\2\u010e\u010f\7\3\2\2\u010f\u0111\7\16")
        buf.write("\2\2\u0110\u0112\5\"\22\2\u0111\u0110\3\2\2\2\u0112\u0113")
        buf.write("\3\2\2\2\u0113\u0111\3\2\2\2\u0113\u0114\3\2\2\2\u0114")
        buf.write("\u0115\3\2\2\2\u0115\u0116\7\5\2\2\u0116!\3\2\2\2\u0117")
        buf.write("\u0118\7\3\2\2\u0118\u0119\5$\23\2\u0119\u011a\5&\24\2")
        buf.write("\u011a\u011b\7\5\2\2\u011b#\3\2\2\2\u011c\u011d\7G\2\2")
        buf.write("\u011d%\3\2\2\2\u011e\u0120\7H\2\2\u011f\u011e\3\2\2\2")
        buf.write("\u0120\u0123\3\2\2\2\u0121\u011f\3\2\2\2\u0121\u0122\3")
        buf.write("\2\2\2\u0122\u0130\3\2\2\2\u0123\u0121\3\2\2\2\u0124\u0126")
        buf.write("\5(\25\2\u0125\u0124\3\2\2\2\u0126\u0127\3\2\2\2\u0127")
        buf.write("\u0125\3\2\2\2\u0127\u0128\3\2\2\2\u0128\u012c\3\2\2\2")
        buf.write("\u0129\u012b\7H\2\2\u012a\u0129\3\2\2\2\u012b\u012e\3")
        buf.write("\2\2\2\u012c\u012a\3\2\2\2\u012c\u012d\3\2\2\2\u012d\u0130")
        buf.write("\3\2\2\2\u012e\u012c\3\2\2\2\u012f\u0121\3\2\2\2\u012f")
        buf.write("\u0125\3\2\2\2\u0130\'\3\2\2\2\u0131\u0133\7H\2\2\u0132")
        buf.write("\u0131\3\2\2\2\u0133\u0134\3\2\2\2\u0134\u0132\3\2\2\2")
        buf.write("\u0134\u0135\3\2\2\2\u0135\u0136\3\2\2\2\u0136\u0137\7")
        buf.write("\t\2\2\u0137\u0138\5\20\t\2\u0138)\3\2\2\2\u0139\u013a")
        buf.write("\7\3\2\2\u013a\u013b\7\17\2\2\u013b\u013c\5\u008eH\2\u013c")
        buf.write("\u013d\7\5\2\2\u013d+\3\2\2\2\u013e\u0142\5.\30\2\u013f")
        buf.write("\u0142\5> \2\u0140\u0142\5L\'\2\u0141\u013e\3\2\2\2\u0141")
        buf.write("\u013f\3\2\2\2\u0141\u0140\3\2\2\2\u0142-\3\2\2\2\u0143")
        buf.write("\u0144\7\3\2\2\u0144\u0145\7\20\2\2\u0145\u0146\5\60\31")
        buf.write("\2\u0146\u0147\7\21\2\2\u0147\u0148\7\3\2\2\u0148\u0149")
        buf.write("\5&\24\2\u0149\u014a\7\5\2\2\u014a\u014b\5\62\32\2\u014b")
        buf.write("\u014c\7\5\2\2\u014c/\3\2\2\2\u014d\u014e\7G\2\2\u014e")
        buf.write("\61\3\2\2\2\u014f\u0153\7\22\2\2\u0150\u0151\7\3\2\2\u0151")
        buf.write("\u0154\7\5\2\2\u0152\u0154\5\64\33\2\u0153\u0150\3\2\2")
        buf.write("\2\u0153\u0152\3\2\2\2\u0154\u0156\3\2\2\2\u0155\u014f")
        buf.write("\3\2\2\2\u0155\u0156\3\2\2\2\u0156\u015d\3\2\2\2\u0157")
        buf.write("\u015b\7\23\2\2\u0158\u0159\7\3\2\2\u0159\u015c\7\5\2")
        buf.write("\2\u015a\u015c\5T+\2\u015b\u0158\3\2\2\2\u015b\u015a\3")
        buf.write("\2\2\2\u015c\u015e\3\2\2\2\u015d\u0157\3\2\2\2\u015d\u015e")
        buf.write("\3\2\2\2\u015e\63\3\2\2\2\u015f\u0160\5\66\34\2\u0160")
        buf.write("\65\3\2\2\2\u0161\u0191\5:\36\2\u0162\u0163\7\3\2\2\u0163")
        buf.write("\u0167\7\24\2\2\u0164\u0166\5\66\34\2\u0165\u0164\3\2")
        buf.write("\2\2\u0166\u0169\3\2\2\2\u0167\u0165\3\2\2\2\u0167\u0168")
        buf.write("\3\2\2\2\u0168\u016a\3\2\2\2\u0169\u0167\3\2\2\2\u016a")
        buf.write("\u0191\7\5\2\2\u016b\u016c\7\3\2\2\u016c\u0170\7\25\2")
        buf.write("\2\u016d\u016f\5\66\34\2\u016e\u016d\3\2\2\2\u016f\u0172")
        buf.write("\3\2\2\2\u0170\u016e\3\2\2\2\u0170\u0171\3\2\2\2\u0171")
        buf.write("\u0173\3\2\2\2\u0172\u0170\3\2\2\2\u0173\u0191\7\5\2\2")
        buf.write("\u0174\u0175\7\3\2\2\u0175\u0176\7\26\2\2\u0176\u0177")
        buf.write("\5\66\34\2\u0177\u0178\7\5\2\2\u0178\u0191\3\2\2\2\u0179")
        buf.write("\u017a\7\3\2\2\u017a\u017b\7\27\2\2\u017b\u017c\5\66\34")
        buf.write("\2\u017c\u017d\5\66\34\2\u017d\u017e\7\5\2\2\u017e\u0191")
        buf.write("\3\2\2\2\u017f\u0180\7\3\2\2\u0180\u0181\7\30\2\2\u0181")
        buf.write("\u0182\7\3\2\2\u0182\u0183\5&\24\2\u0183\u0184\7\5\2\2")
        buf.write("\u0184\u0185\5\66\34\2\u0185\u0186\7\5\2\2\u0186\u0191")
        buf.write("\3\2\2\2\u0187\u0188\7\3\2\2\u0188\u0189\7\31\2\2\u0189")
        buf.write("\u018a\7\3\2\2\u018a\u018b\5&\24\2\u018b\u018c\7\5\2\2")
        buf.write("\u018c\u018d\5\66\34\2\u018d\u018e\7\5\2\2\u018e\u0191")
        buf.write("\3\2\2\2\u018f\u0191\58\35\2\u0190\u0161\3\2\2\2\u0190")
        buf.write("\u0162\3\2\2\2\u0190\u016b\3\2\2\2\u0190\u0174\3\2\2\2")
        buf.write("\u0190\u0179\3\2\2\2\u0190\u017f\3\2\2\2\u0190\u0187\3")
        buf.write("\2\2\2\u0190\u018f\3\2\2\2\u0191\67\3\2\2\2\u0192\u0193")
        buf.write("\7\3\2\2\u0193\u0194\5^\60\2\u0194\u0195\5N(\2\u0195\u0196")
        buf.write("\5N(\2\u0196\u0197\7\5\2\2\u01979\3\2\2\2\u0198\u0199")
        buf.write("\7\3\2\2\u0199\u019d\5$\23\2\u019a\u019c\5<\37\2\u019b")
        buf.write("\u019a\3\2\2\2\u019c\u019f\3\2\2\2\u019d\u019b\3\2\2\2")
        buf.write("\u019d\u019e\3\2\2\2\u019e\u01a0\3\2\2\2\u019f\u019d\3")
        buf.write("\2\2\2\u01a0\u01a1\7\5\2\2\u01a1;\3\2\2\2\u01a2\u01a3")
        buf.write("\t\2\2\2\u01a3=\3\2\2\2\u01a4\u01a5\7\3\2\2\u01a5\u01a6")
        buf.write("\7\32\2\2\u01a6\u01a7\5\60\31\2\u01a7\u01a8\7\21\2\2\u01a8")
        buf.write("\u01a9\7\3\2\2\u01a9\u01aa\5&\24\2\u01aa\u01ab\7\5\2\2")
        buf.write("\u01ab\u01ac\5@!\2\u01ac\u01ad\7\5\2\2\u01ad?\3\2\2\2")
        buf.write("\u01ae\u01af\7\33\2\2\u01af\u01bd\5b\62\2\u01b0\u01b4")
        buf.write("\7\34\2\2\u01b1\u01b2\7\3\2\2\u01b2\u01b5\7\5\2\2\u01b3")
        buf.write("\u01b5\5B\"\2\u01b4\u01b1\3\2\2\2\u01b4\u01b3\3\2\2\2")
        buf.write("\u01b5\u01bd\3\2\2\2\u01b6\u01ba\7\23\2\2\u01b7\u01b8")
        buf.write("\7\3\2\2\u01b8\u01bb\7\5\2\2\u01b9\u01bb\5j\66\2\u01ba")
        buf.write("\u01b7\3\2\2\2\u01ba\u01b9\3\2\2\2\u01bb\u01bd\3\2\2\2")
        buf.write("\u01bc\u01ae\3\2\2\2\u01bc\u01b0\3\2\2\2\u01bc\u01b6\3")
        buf.write("\2\2\2\u01bdA\3\2\2\2\u01be\u01d1\5D#\2\u01bf\u01c0\7")
        buf.write("\3\2\2\u01c0\u01c4\7\24\2\2\u01c1\u01c3\5B\"\2\u01c2\u01c1")
        buf.write("\3\2\2\2\u01c3\u01c6\3\2\2\2\u01c4\u01c2\3\2\2\2\u01c4")
        buf.write("\u01c5\3\2\2\2\u01c5\u01c7\3\2\2\2\u01c6\u01c4\3\2\2\2")
        buf.write("\u01c7\u01d1\7\5\2\2\u01c8\u01c9\7\3\2\2\u01c9\u01ca\7")
        buf.write("\31\2\2\u01ca\u01cb\7\3\2\2\u01cb\u01cc\5&\24\2\u01cc")
        buf.write("\u01cd\7\5\2\2\u01cd\u01ce\5B\"\2\u01ce\u01cf\7\5\2\2")
        buf.write("\u01cf\u01d1\3\2\2\2\u01d0\u01be\3\2\2\2\u01d0\u01bf\3")
        buf.write("\2\2\2\u01d0\u01c8\3\2\2\2\u01d1C\3\2\2\2\u01d2\u01dc")
        buf.write("\5F$\2\u01d3\u01d4\7\3\2\2\u01d4\u01d6\7\35\2\2\u01d5")
        buf.write("\u01d7\7G\2\2\u01d6\u01d5\3\2\2\2\u01d6\u01d7\3\2\2\2")
        buf.write("\u01d7\u01d8\3\2\2\2\u01d8\u01d9\5F$\2\u01d9\u01da\7\5")
        buf.write("\2\2\u01da\u01dc\3\2\2\2\u01db\u01d2\3\2\2\2\u01db\u01d3")
        buf.write("\3\2\2\2\u01dcE\3\2\2\2\u01dd\u01de\7\3\2\2\u01de\u01df")
        buf.write("\7\36\2\2\u01df\u01e0\5H%\2\u01e0\u01e1\5\66\34\2\u01e1")
        buf.write("\u01e2\7\5\2\2\u01e2\u01ea\3\2\2\2\u01e3\u01e4\7\3\2\2")
        buf.write("\u01e4\u01e5\7\37\2\2\u01e5\u01e6\5J&\2\u01e6\u01e7\5")
        buf.write("\66\34\2\u01e7\u01e8\7\5\2\2\u01e8\u01ea\3\2\2\2\u01e9")
        buf.write("\u01dd\3\2\2\2\u01e9\u01e3\3\2\2\2\u01eaG\3\2\2\2\u01eb")
        buf.write("\u01ec\t\3\2\2\u01ecI\3\2\2\2\u01ed\u01ee\7\"\2\2\u01ee")
        buf.write("K\3\2\2\2\u01ef\u01f0\7\3\2\2\u01f0\u01f1\7#\2\2\u01f1")
        buf.write("\u01f2\5&\24\2\u01f2\u01f3\5\66\34\2\u01f3\u01f4\7\5\2")
        buf.write("\2\u01f4M\3\2\2\2\u01f5\u0203\7I\2\2\u01f6\u01f7\7\3\2")
        buf.write("\2\u01f7\u01f8\5\\/\2\u01f8\u01f9\5N(\2\u01f9\u01fa\5")
        buf.write("P)\2\u01fa\u01fb\7\5\2\2\u01fb\u0203\3\2\2\2\u01fc\u01fd")
        buf.write("\7\3\2\2\u01fd\u01fe\7\t\2\2\u01fe\u01ff\5N(\2\u01ff\u0200")
        buf.write("\7\5\2\2\u0200\u0203\3\2\2\2\u0201\u0203\5R*\2\u0202\u01f5")
        buf.write("\3\2\2\2\u0202\u01f6\3\2\2\2\u0202\u01fc\3\2\2\2\u0202")
        buf.write("\u0201\3\2\2\2\u0203O\3\2\2\2\u0204\u0205\5N(\2\u0205")
        buf.write("Q\3\2\2\2\u0206\u0207\7\3\2\2\u0207\u020b\5\32\16\2\u0208")
        buf.write("\u020a\5<\37\2\u0209\u0208\3\2\2\2\u020a\u020d\3\2\2\2")
        buf.write("\u020b\u0209\3\2\2\2\u020b\u020c\3\2\2\2\u020c\u020e\3")
        buf.write("\2\2\2\u020d\u020b\3\2\2\2\u020e\u020f\7\5\2\2\u020f\u0212")
        buf.write("\3\2\2\2\u0210\u0212\5\32\16\2\u0211\u0206\3\2\2\2\u0211")
        buf.write("\u0210\3\2\2\2\u0212S\3\2\2\2\u0213\u0214\7\3\2\2\u0214")
        buf.write("\u0218\7\24\2\2\u0215\u0217\5V,\2\u0216\u0215\3\2\2\2")
        buf.write("\u0217\u021a\3\2\2\2\u0218\u0216\3\2\2\2\u0218\u0219\3")
        buf.write("\2\2\2\u0219\u021b\3\2\2\2\u021a\u0218\3\2\2\2\u021b\u021e")
        buf.write("\7\5\2\2\u021c\u021e\5V,\2\u021d\u0213\3\2\2\2\u021d\u021c")
        buf.write("\3\2\2\2\u021eU\3\2\2\2\u021f\u0220\7\3\2\2\u0220\u0221")
        buf.write("\7\31\2\2\u0221\u0222\7\3\2\2\u0222\u0223\5&\24\2\u0223")
        buf.write("\u0224\7\5\2\2\u0224\u0225\5T+\2\u0225\u0226\7\5\2\2\u0226")
        buf.write("\u022f\3\2\2\2\u0227\u0228\7\3\2\2\u0228\u0229\7$\2\2")
        buf.write("\u0229\u022a\5\66\34\2\u022a\u022b\5Z.\2\u022b\u022c\7")
        buf.write("\5\2\2\u022c\u022f\3\2\2\2\u022d\u022f\5X-\2\u022e\u021f")
        buf.write("\3\2\2\2\u022e\u0227\3\2\2\2\u022e\u022d\3\2\2\2\u022f")
        buf.write("W\3\2\2\2\u0230\u0231\7\3\2\2\u0231\u0232\5`\61\2\u0232")
        buf.write("\u0233\5R*\2\u0233\u0234\5N(\2\u0234\u0235\7\5\2\2\u0235")
        buf.write("\u023d\3\2\2\2\u0236\u0237\7\3\2\2\u0237\u0238\7\26\2")
        buf.write("\2\u0238\u0239\5:\36\2\u0239\u023a\7\5\2\2\u023a\u023d")
        buf.write("\3\2\2\2\u023b\u023d\5:\36\2\u023c\u0230\3\2\2\2\u023c")
        buf.write("\u0236\3\2\2\2\u023c\u023b\3\2\2\2\u023dY\3\2\2\2\u023e")
        buf.write("\u023f\7\3\2\2\u023f\u0243\7\24\2\2\u0240\u0242\5X-\2")
        buf.write("\u0241\u0240\3\2\2\2\u0242\u0245\3\2\2\2\u0243\u0241\3")
        buf.write("\2\2\2\u0243\u0244\3\2\2\2\u0244\u0246\3\2\2\2\u0245\u0243")
        buf.write("\3\2\2\2\u0246\u0249\7\5\2\2\u0247\u0249\5X-\2\u0248\u023e")
        buf.write("\3\2\2\2\u0248\u0247\3\2\2\2\u0249[\3\2\2\2\u024a\u024b")
        buf.write("\t\4\2\2\u024b]\3\2\2\2\u024c\u024d\t\5\2\2\u024d_\3\2")
        buf.write("\2\2\u024e\u024f\t\6\2\2\u024fa\3\2\2\2\u0250\u0251\7")
        buf.write("\3\2\2\u0251\u0253\7\24\2\2\u0252\u0254\5d\63\2\u0253")
        buf.write("\u0252\3\2\2\2\u0254\u0255\3\2\2\2\u0255\u0253\3\2\2\2")
        buf.write("\u0255\u0256\3\2\2\2\u0256\u0257\3\2\2\2\u0257\u0258\7")
        buf.write("\5\2\2\u0258\u025d\3\2\2\2\u0259\u025a\7\3\2\2\u025a\u025d")
        buf.write("\7\5\2\2\u025b\u025d\5d\63\2\u025c\u0250\3\2\2\2\u025c")
        buf.write("\u0259\3\2\2\2\u025c\u025b\3\2\2\2\u025dc\3\2\2\2\u025e")
        buf.write("\u025f\7\3\2\2\u025f\u0260\5f\64\2\u0260\u0261\7\62\2")
        buf.write("\2\u0261\u0262\5h\65\2\u0262\u0263\7\5\2\2\u0263\u026b")
        buf.write("\3\2\2\2\u0264\u0265\7\3\2\2\u0265\u0266\7\36\2\2\u0266")
        buf.write("\u0267\5H%\2\u0267\u0268\5d\63\2\u0268\u0269\7\5\2\2\u0269")
        buf.write("\u026b\3\2\2\2\u026a\u025e\3\2\2\2\u026a\u0264\3\2\2\2")
        buf.write("\u026be\3\2\2\2\u026c\u026d\t\7\2\2\u026dg\3\2\2\2\u026e")
        buf.write("\u0271\7I\2\2\u026f\u0271\5N(\2\u0270\u026e\3\2\2\2\u0270")
        buf.write("\u026f\3\2\2\2\u0271i\3\2\2\2\u0272\u0273\7\3\2\2\u0273")
        buf.write("\u0277\7\24\2\2\u0274\u0276\5j\66\2\u0275\u0274\3\2\2")
        buf.write("\2\u0276\u0279\3\2\2\2\u0277\u0275\3\2\2\2\u0277\u0278")
        buf.write("\3\2\2\2\u0278\u027a\3\2\2\2\u0279\u0277\3\2\2\2\u027a")
        buf.write("\u0291\7\5\2\2\u027b\u0291\5l\67\2\u027c\u027d\7\3\2\2")
        buf.write("\u027d\u027e\7\31\2\2\u027e\u027f\7\3\2\2\u027f\u0280")
        buf.write("\5&\24\2\u0280\u0281\7\5\2\2\u0281\u0282\5j\66\2\u0282")
        buf.write("\u0283\7\5\2\2\u0283\u0291\3\2\2\2\u0284\u0285\7\3\2\2")
        buf.write("\u0285\u0286\7$\2\2\u0286\u0287\5B\"\2\u0287\u0288\5l")
        buf.write("\67\2\u0288\u0289\7\5\2\2\u0289\u0291\3\2\2\2\u028a\u028b")
        buf.write("\7\3\2\2\u028b\u028c\5`\61\2\u028c\u028d\5R*\2\u028d\u028e")
        buf.write("\5p9\2\u028e\u028f\7\5\2\2\u028f\u0291\3\2\2\2\u0290\u0272")
        buf.write("\3\2\2\2\u0290\u027b\3\2\2\2\u0290\u027c\3\2\2\2\u0290")
        buf.write("\u0284\3\2\2\2\u0290\u028a\3\2\2\2\u0291k\3\2\2\2\u0292")
        buf.write("\u0293\7\3\2\2\u0293\u0294\7\36\2\2\u0294\u0295\5H%\2")
        buf.write("\u0295\u0296\5j\66\2\u0296\u0297\7\5\2\2\u0297\u02a5\3")
        buf.write("\2\2\2\u0298\u0299\7\3\2\2\u0299\u029a\7\36\2\2\u029a")
        buf.write("\u029b\5H%\2\u029b\u029c\5n8\2\u029c\u029d\7\5\2\2\u029d")
        buf.write("\u02a5\3\2\2\2\u029e\u029f\7\3\2\2\u029f\u02a0\5`\61\2")
        buf.write("\u02a0\u02a1\5R*\2\u02a1\u02a2\5N(\2\u02a2\u02a3\7\5\2")
        buf.write("\2\u02a3\u02a5\3\2\2\2\u02a4\u0292\3\2\2\2\u02a4\u0298")
        buf.write("\3\2\2\2\u02a4\u029e\3\2\2\2\u02a5m\3\2\2\2\u02a6\u02a7")
        buf.write("\7\3\2\2\u02a7\u02a8\5`\61\2\u02a8\u02a9\5R*\2\u02a9\u02aa")
        buf.write("\5p9\2\u02aa\u02ab\7\5\2\2\u02abo\3\2\2\2\u02ac\u02b3")
        buf.write("\7\3\2\2\u02ad\u02ae\5\\/\2\u02ae\u02af\5p9\2\u02af\u02b0")
        buf.write("\5p9\2\u02b0\u02b4\3\2\2\2\u02b1\u02b2\7\t\2\2\u02b2\u02b4")
        buf.write("\5p9\2\u02b3\u02ad\3\2\2\2\u02b3\u02b1\3\2\2\2\u02b4\u02b5")
        buf.write("\3\2\2\2\u02b5\u02b6\7\5\2\2\u02b6\u02ba\3\2\2\2\u02b7")
        buf.write("\u02ba\7\62\2\2\u02b8\u02ba\5N(\2\u02b9\u02ac\3\2\2\2")
        buf.write("\u02b9\u02b7\3\2\2\2\u02b9\u02b8\3\2\2\2\u02baq\3\2\2")
        buf.write("\2\u02bb\u02bc\7\3\2\2\u02bc\u02bd\7\4\2\2\u02bd\u02be")
        buf.write("\5t;\2\u02be\u02c0\5v<\2\u02bf\u02c1\5\b\5\2\u02c0\u02bf")
        buf.write("\3\2\2\2\u02c0\u02c1\3\2\2\2\u02c1\u02c3\3\2\2\2\u02c2")
        buf.write("\u02c4\5x=\2\u02c3\u02c2\3\2\2\2\u02c3\u02c4\3\2\2\2\u02c4")
        buf.write("\u02c5\3\2\2\2\u02c5\u02c6\5z>\2\u02c6\u02c8\5\u0082B")
        buf.write("\2\u02c7\u02c9\5\u0084C\2\u02c8\u02c7\3\2\2\2\u02c8\u02c9")
        buf.write("\3\2\2\2\u02c9\u02cb\3\2\2\2\u02ca\u02cc\5\u0088E\2\u02cb")
        buf.write("\u02ca\3\2\2\2\u02cb\u02cc\3\2\2\2\u02cc\u02cd\3\2\2\2")
        buf.write("\u02cd\u02ce\7\5\2\2\u02ces\3\2\2\2\u02cf\u02d0\7\3\2")
        buf.write("\2\u02d0\u02d1\7\63\2\2\u02d1\u02d2\7G\2\2\u02d2\u02d3")
        buf.write("\7\5\2\2\u02d3u\3\2\2\2\u02d4\u02d5\7\3\2\2\u02d5\u02d6")
        buf.write("\7\64\2\2\u02d6\u02d7\7G\2\2\u02d7\u02d8\7\5\2\2\u02d8")
        buf.write("w\3\2\2\2\u02d9\u02da\7\3\2\2\u02da\u02db\7\65\2\2\u02db")
        buf.write("\u02dc\5\f\7\2\u02dc\u02dd\7\5\2\2\u02ddy\3\2\2\2\u02de")
        buf.write("\u02df\7\3\2\2\u02df\u02e3\7\66\2\2\u02e0\u02e2\5|?\2")
        buf.write("\u02e1\u02e0\3\2\2\2\u02e2\u02e5\3\2\2\2\u02e3\u02e1\3")
        buf.write("\2\2\2\u02e3\u02e4\3\2\2\2\u02e4\u02e6\3\2\2\2\u02e5\u02e3")
        buf.write("\3\2\2\2\u02e6\u02e7\7\5\2\2\u02e7{\3\2\2\2\u02e8\u02f6")
        buf.write("\5~@\2\u02e9\u02ea\7\3\2\2\u02ea\u02eb\7*\2\2\u02eb\u02ec")
        buf.write("\5R*\2\u02ec\u02ed\7I\2\2\u02ed\u02ee\7\5\2\2\u02ee\u02f6")
        buf.write("\3\2\2\2\u02ef\u02f0\7\3\2\2\u02f0\u02f1\7\36\2\2\u02f1")
        buf.write("\u02f2\7I\2\2\u02f2\u02f3\5~@\2\u02f3\u02f4\7\5\2\2\u02f4")
        buf.write("\u02f6\3\2\2\2\u02f5\u02e8\3\2\2\2\u02f5\u02e9\3\2\2\2")
        buf.write("\u02f5\u02ef\3\2\2\2\u02f6}\3\2\2\2\u02f7\u02fe\5\u0080")
        buf.write("A\2\u02f8\u02f9\7\3\2\2\u02f9\u02fa\7\26\2\2\u02fa\u02fb")
        buf.write("\5\u0080A\2\u02fb\u02fc\7\5\2\2\u02fc\u02fe\3\2\2\2\u02fd")
        buf.write("\u02f7\3\2\2\2\u02fd\u02f8\3\2\2\2\u02fe\177\3\2\2\2\u02ff")
        buf.write("\u0300\7\3\2\2\u0300\u0304\5$\23\2\u0301\u0303\7G\2\2")
        buf.write("\u0302\u0301\3\2\2\2\u0303\u0306\3\2\2\2\u0304\u0302\3")
        buf.write("\2\2\2\u0304\u0305\3\2\2\2\u0305\u0307\3\2\2\2\u0306\u0304")
        buf.write("\3\2\2\2\u0307\u0308\7\5\2\2\u0308\u0081\3\2\2\2\u0309")
        buf.write("\u030a\7\3\2\2\u030a\u030b\7\67\2\2\u030b\u030c\5\66\34")
        buf.write("\2\u030c\u030d\7\5\2\2\u030d\u0083\3\2\2\2\u030e\u030f")
        buf.write("\7\3\2\2\u030f\u0310\7\17\2\2\u0310\u0311\5\u0086D\2\u0311")
        buf.write("\u0312\7\5\2\2\u0312\u0085\3\2\2\2\u0313\u0314\7\3\2\2")
        buf.write("\u0314\u0318\7\24\2\2\u0315\u0317\5\u0086D\2\u0316\u0315")
        buf.write("\3\2\2\2\u0317\u031a\3\2\2\2\u0318\u0316\3\2\2\2\u0318")
        buf.write("\u0319\3\2\2\2\u0319\u031b\3\2\2\2\u031a\u0318\3\2\2\2")
        buf.write("\u031b\u032e\7\5\2\2\u031c\u031d\7\3\2\2\u031d\u031e\7")
        buf.write("\31\2\2\u031e\u031f\7\3\2\2\u031f\u0320\5&\24\2\u0320")
        buf.write("\u0321\7\5\2\2\u0321\u0322\5\u0086D\2\u0322\u0323\7\5")
        buf.write("\2\2\u0323\u032e\3\2\2\2\u0324\u0325\7\3\2\2\u0325\u0327")
        buf.write("\7\35\2\2\u0326\u0328\7G\2\2\u0327\u0326\3\2\2\2\u0327")
        buf.write("\u0328\3\2\2\2\u0328\u0329\3\2\2\2\u0329\u032a\5\u008e")
        buf.write("H\2\u032a\u032b\7\5\2\2\u032b\u032e\3\2\2\2\u032c\u032e")
        buf.write("\5\u008eH\2\u032d\u0313\3\2\2\2\u032d\u031c\3\2\2\2\u032d")
        buf.write("\u0324\3\2\2\2\u032d\u032c\3\2\2\2\u032e\u0087\3\2\2\2")
        buf.write("\u032f\u0330\7\3\2\2\u0330\u0331\78\2\2\u0331\u0332\5")
        buf.write("\u008aF\2\u0332\u0333\5\u008cG\2\u0333\u0334\7\5\2\2\u0334")
        buf.write("\u0089\3\2\2\2\u0335\u0336\t\b\2\2\u0336\u008b\3\2\2\2")
        buf.write("\u0337\u0338\7\3\2\2\u0338\u0339\5\\/\2\u0339\u033a\5")
        buf.write("\u008cG\2\u033a\u033b\5\u008cG\2\u033b\u033c\7\5\2\2\u033c")
        buf.write("\u035e\3\2\2\2\u033d\u033e\7\3\2\2\u033e\u033f\t\t\2\2")
        buf.write("\u033f\u0341\5\u008cG\2\u0340\u0342\5\u008cG\2\u0341\u0340")
        buf.write("\3\2\2\2\u0342\u0343\3\2\2\2\u0343\u0341\3\2\2\2\u0343")
        buf.write("\u0344\3\2\2\2\u0344\u0345\3\2\2\2\u0345\u0346\7\5\2\2")
        buf.write("\u0346\u035e\3\2\2\2\u0347\u0348\7\3\2\2\u0348\u0349\7")
        buf.write("\t\2\2\u0349\u034a\5\u008cG\2\u034a\u034b\7\5\2\2\u034b")
        buf.write("\u035e\3\2\2\2\u034c\u035e\7I\2\2\u034d\u034e\7\3\2\2")
        buf.write("\u034e\u0352\5\32\16\2\u034f\u0351\7G\2\2\u0350\u034f")
        buf.write("\3\2\2\2\u0351\u0354\3\2\2\2\u0352\u0350\3\2\2\2\u0352")
        buf.write("\u0353\3\2\2\2\u0353\u0355\3\2\2\2\u0354\u0352\3\2\2\2")
        buf.write("\u0355\u0356\7\5\2\2\u0356\u035e\3\2\2\2\u0357\u035e\5")
        buf.write("\32\16\2\u0358\u035e\7;\2\2\u0359\u035a\7\3\2\2\u035a")
        buf.write("\u035b\7<\2\2\u035b\u035c\7G\2\2\u035c\u035e\7\5\2\2\u035d")
        buf.write("\u0337\3\2\2\2\u035d\u033d\3\2\2\2\u035d\u0347\3\2\2\2")
        buf.write("\u035d\u034c\3\2\2\2\u035d\u034d\3\2\2\2\u035d\u0357\3")
        buf.write("\2\2\2\u035d\u0358\3\2\2\2\u035d\u0359\3\2\2\2\u035e\u008d")
        buf.write("\3\2\2\2\u035f\u0360\7\3\2\2\u0360\u0364\7\24\2\2\u0361")
        buf.write("\u0363\5\u008eH\2\u0362\u0361\3\2\2\2\u0363\u0366\3\2")
        buf.write("\2\2\u0364\u0362\3\2\2\2\u0364\u0365\3\2\2\2\u0365\u0367")
        buf.write("\3\2\2\2\u0366\u0364\3\2\2\2\u0367\u03ac\7\5\2\2\u0368")
        buf.write("\u0369\7\3\2\2\u0369\u036a\7\31\2\2\u036a\u036b\7\3\2")
        buf.write("\2\u036b\u036c\5&\24\2\u036c\u036d\7\5\2\2\u036d\u036e")
        buf.write("\5\u008eH\2\u036e\u036f\7\5\2\2\u036f\u03ac\3\2\2\2\u0370")
        buf.write("\u0371\7\3\2\2\u0371\u0372\7\36\2\2\u0372\u0373\7!\2\2")
        buf.write("\u0373\u0374\5\66\34\2\u0374\u0375\7\5\2\2\u0375\u03ac")
        buf.write("\3\2\2\2\u0376\u0377\7\3\2\2\u0377\u0378\7=\2\2\u0378")
        buf.write("\u0379\5\66\34\2\u0379\u037a\7\5\2\2\u037a\u03ac\3\2\2")
        buf.write("\2\u037b\u037c\7\3\2\2\u037c\u037d\7>\2\2\u037d\u037e")
        buf.write("\5\66\34\2\u037e\u037f\7\5\2\2\u037f\u03ac\3\2\2\2\u0380")
        buf.write("\u0381\7\3\2\2\u0381\u0382\7?\2\2\u0382\u0383\7I\2\2\u0383")
        buf.write("\u0384\5\66\34\2\u0384\u0385\7\5\2\2\u0385\u03ac\3\2\2")
        buf.write("\2\u0386\u0387\7\3\2\2\u0387\u0388\7@\2\2\u0388\u0389")
        buf.write("\5\66\34\2\u0389\u038a\7\5\2\2\u038a\u03ac\3\2\2\2\u038b")
        buf.write("\u038c\7\3\2\2\u038c\u038d\7A\2\2\u038d\u038e\5\66\34")
        buf.write("\2\u038e\u038f\5\66\34\2\u038f\u0390\7\5\2\2\u0390\u03ac")
        buf.write("\3\2\2\2\u0391\u0392\7\3\2\2\u0392\u0393\7B\2\2\u0393")
        buf.write("\u0394\5\66\34\2\u0394\u0395\5\66\34\2\u0395\u0396\7\5")
        buf.write("\2\2\u0396\u03ac\3\2\2\2\u0397\u0398\7\3\2\2\u0398\u0399")
        buf.write("\7C\2\2\u0399\u039a\7I\2\2\u039a\u039b\5\66\34\2\u039b")
        buf.write("\u039c\5\66\34\2\u039c\u039d\7\5\2\2\u039d\u03ac\3\2\2")
        buf.write("\2\u039e\u039f\7\3\2\2\u039f\u03a0\7D\2\2\u03a0\u03a1")
        buf.write("\7I\2\2\u03a1\u03a2\7I\2\2\u03a2\u03a3\5\66\34\2\u03a3")
        buf.write("\u03a4\7\5\2\2\u03a4\u03ac\3\2\2\2\u03a5\u03a6\7\3\2\2")
        buf.write("\u03a6\u03a7\7E\2\2\u03a7\u03a8\7I\2\2\u03a8\u03a9\5\66")
        buf.write("\34\2\u03a9\u03aa\7\5\2\2\u03aa\u03ac\3\2\2\2\u03ab\u035f")
        buf.write("\3\2\2\2\u03ab\u0368\3\2\2\2\u03ab\u0370\3\2\2\2\u03ab")
        buf.write("\u0376\3\2\2\2\u03ab\u037b\3\2\2\2\u03ab\u0380\3\2\2\2")
        buf.write("\u03ab\u0386\3\2\2\2\u03ab\u038b\3\2\2\2\u03ab\u0391\3")
        buf.write("\2\2\2\u03ab\u0397\3\2\2\2\u03ab\u039e\3\2\2\2\u03ab\u03a5")
        buf.write("\3\2\2\2\u03ac\u008f\3\2\2\2N\u0092\u0098\u009b\u009e")
        buf.write("\u00a1\u00a4\u00a7\u00ac\u00bb\u00c7\u00cd\u00d2\u00d5")
        buf.write("\u00da\u00e4\u00e9\u00f5\u00f9\u00fd\u0113\u0121\u0127")
        buf.write("\u012c\u012f\u0134\u0141\u0153\u0155\u015b\u015d\u0167")
        buf.write("\u0170\u0190\u019d\u01b4\u01ba\u01bc\u01c4\u01d0\u01d6")
        buf.write("\u01db\u01e9\u0202\u020b\u0211\u0218\u021d\u022e\u023c")
        buf.write("\u0243\u0248\u0255\u025c\u026a\u0270\u0277\u0290\u02a4")
        buf.write("\u02b3\u02b9\u02c0\u02c3\u02c8\u02cb\u02e3\u02f5\u02fd")
        buf.write("\u0304\u0318\u0327\u032d\u0343\u0352\u035d\u0364\u03ab")
        return buf.getvalue()


class pddlParser ( Parser ):

    grammarFileName = "java-escape"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ u"<INVALID>", u"'('", u"'define'", u"')'", u"'domain'", 
                     u"':requirements'", u"':types'", u"'-'", u"'either'", 
                     u"':functions'", u"'number'", u"':constants'", u"':predicates'", 
                     u"':constraints'", u"':action'", u"':parameters'", 
                     u"':precondition'", u"':effect'", u"'and'", u"'or'", 
                     u"'not'", u"'imply'", u"'exists'", u"'forall'", u"':durative-action'", 
                     u"':duration'", u"':condition'", u"'preference'", u"'at'", 
                     u"'over'", u"'start'", u"'end'", u"'all'", u"':derived'", 
                     u"'when'", u"'*'", u"'+'", u"'/'", u"'>'", u"'<'", 
                     u"'='", u"'>='", u"'<='", u"'assign'", u"'scale-up'", 
                     u"'scale-down'", u"'increase'", u"'decrease'", u"'?duration'", 
                     u"'problem'", u"':domain'", u"':objects'", u"':init'", 
                     u"':goal'", u"':metric'", u"'minimize'", u"'maximize'", 
                     u"'total-time'", u"'is-violated'", u"'always'", u"'sometime'", 
                     u"'within'", u"'at-most-once'", u"'sometime-after'", 
                     u"'sometime-before'", u"'always-within'", u"'hold-during'", 
                     u"'hold-after'" ]

    symbolicNames = [ u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"<INVALID>", u"<INVALID>", u"<INVALID>", u"<INVALID>", 
                      u"REQUIRE_KEY", u"NAME", u"VARIABLE", u"NUMBER", u"LINE_COMMENT", 
                      u"WHITESPACE", u"DOMAIN", u"DOMAIN_NAME", u"REQUIREMENTS", 
                      u"TYPES", u"EITHER_TYPE", u"CONSTANTS", u"FUNCTIONS", 
                      u"PREDICATES", u"ACTION", u"DURATIVE_ACTION", u"PROBLEM", 
                      u"PROBLEM_NAME", u"PROBLEM_DOMAIN", u"OBJECTS", u"INIT", 
                      u"FUNC_HEAD", u"PRECONDITION", u"EFFECT", u"AND_GD", 
                      u"OR_GD", u"NOT_GD", u"IMPLY_GD", u"EXISTS_GD", u"FORALL_GD", 
                      u"COMPARISON_GD", u"AND_EFFECT", u"FORALL_EFFECT", 
                      u"WHEN_EFFECT", u"ASSIGN_EFFECT", u"NOT_EFFECT", u"PRED_HEAD", 
                      u"GOAL", u"BINARY_OP", u"UNARY_MINUS", u"INIT_EQ", 
                      u"INIT_AT", u"NOT_PRED_INIT", u"PRED_INST", u"PROBLEM_CONSTRAINT", 
                      u"PROBLEM_METRIC" ]

    RULE_pddlDoc = 0
    RULE_domain = 1
    RULE_domainName = 2
    RULE_requireDef = 3
    RULE_typesDef = 4
    RULE_typedNameList = 5
    RULE_singleTypeNameList = 6
    RULE_r_type = 7
    RULE_primType = 8
    RULE_functionsDef = 9
    RULE_functionList = 10
    RULE_atomicFunctionSkeleton = 11
    RULE_functionSymbol = 12
    RULE_functionType = 13
    RULE_constantsDef = 14
    RULE_predicatesDef = 15
    RULE_atomicFormulaSkeleton = 16
    RULE_predicate = 17
    RULE_typedVariableList = 18
    RULE_singleTypeVarList = 19
    RULE_constraints = 20
    RULE_structureDef = 21
    RULE_actionDef = 22
    RULE_actionSymbol = 23
    RULE_actionDefBody = 24
    RULE_precondition = 25
    RULE_goalDesc = 26
    RULE_fComp = 27
    RULE_atomicTermFormula = 28
    RULE_term = 29
    RULE_durativeActionDef = 30
    RULE_daDefBody = 31
    RULE_daGD = 32
    RULE_prefTimedGD = 33
    RULE_timedGD = 34
    RULE_timeSpecifier = 35
    RULE_interval = 36
    RULE_derivedDef = 37
    RULE_fExp = 38
    RULE_fExp2 = 39
    RULE_fHead = 40
    RULE_effect = 41
    RULE_cEffect = 42
    RULE_pEffect = 43
    RULE_condEffect = 44
    RULE_binaryOp = 45
    RULE_binaryComp = 46
    RULE_assignOp = 47
    RULE_durationConstraint = 48
    RULE_simpleDurationConstraint = 49
    RULE_durOp = 50
    RULE_durValue = 51
    RULE_daEffect = 52
    RULE_timedEffect = 53
    RULE_fAssignDA = 54
    RULE_fExpDA = 55
    RULE_problem = 56
    RULE_problemDecl = 57
    RULE_problemDomain = 58
    RULE_objectDecl = 59
    RULE_init = 60
    RULE_initEl = 61
    RULE_nameLiteral = 62
    RULE_atomicNameFormula = 63
    RULE_goal = 64
    RULE_probConstraints = 65
    RULE_prefConGD = 66
    RULE_metricSpec = 67
    RULE_optimization = 68
    RULE_metricFExp = 69
    RULE_conGD = 70

    ruleNames =  [ "pddlDoc", "domain", "domainName", "requireDef", "typesDef", 
                   "typedNameList", "singleTypeNameList", "r_type", "primType", 
                   "functionsDef", "functionList", "atomicFunctionSkeleton", 
                   "functionSymbol", "functionType", "constantsDef", "predicatesDef", 
                   "atomicFormulaSkeleton", "predicate", "typedVariableList", 
                   "singleTypeVarList", "constraints", "structureDef", "actionDef", 
                   "actionSymbol", "actionDefBody", "precondition", "goalDesc", 
                   "fComp", "atomicTermFormula", "term", "durativeActionDef", 
                   "daDefBody", "daGD", "prefTimedGD", "timedGD", "timeSpecifier", 
                   "interval", "derivedDef", "fExp", "fExp2", "fHead", "effect", 
                   "cEffect", "pEffect", "condEffect", "binaryOp", "binaryComp", 
                   "assignOp", "durationConstraint", "simpleDurationConstraint", 
                   "durOp", "durValue", "daEffect", "timedEffect", "fAssignDA", 
                   "fExpDA", "problem", "problemDecl", "problemDomain", 
                   "objectDecl", "init", "initEl", "nameLiteral", "atomicNameFormula", 
                   "goal", "probConstraints", "prefConGD", "metricSpec", 
                   "optimization", "metricFExp", "conGD" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    T__17=18
    T__18=19
    T__19=20
    T__20=21
    T__21=22
    T__22=23
    T__23=24
    T__24=25
    T__25=26
    T__26=27
    T__27=28
    T__28=29
    T__29=30
    T__30=31
    T__31=32
    T__32=33
    T__33=34
    T__34=35
    T__35=36
    T__36=37
    T__37=38
    T__38=39
    T__39=40
    T__40=41
    T__41=42
    T__42=43
    T__43=44
    T__44=45
    T__45=46
    T__46=47
    T__47=48
    T__48=49
    T__49=50
    T__50=51
    T__51=52
    T__52=53
    T__53=54
    T__54=55
    T__55=56
    T__56=57
    T__57=58
    T__58=59
    T__59=60
    T__60=61
    T__61=62
    T__62=63
    T__63=64
    T__64=65
    T__65=66
    T__66=67
    REQUIRE_KEY=68
    NAME=69
    VARIABLE=70
    NUMBER=71
    LINE_COMMENT=72
    WHITESPACE=73
    DOMAIN=74
    DOMAIN_NAME=75
    REQUIREMENTS=76
    TYPES=77
    EITHER_TYPE=78
    CONSTANTS=79
    FUNCTIONS=80
    PREDICATES=81
    ACTION=82
    DURATIVE_ACTION=83
    PROBLEM=84
    PROBLEM_NAME=85
    PROBLEM_DOMAIN=86
    OBJECTS=87
    INIT=88
    FUNC_HEAD=89
    PRECONDITION=90
    EFFECT=91
    AND_GD=92
    OR_GD=93
    NOT_GD=94
    IMPLY_GD=95
    EXISTS_GD=96
    FORALL_GD=97
    COMPARISON_GD=98
    AND_EFFECT=99
    FORALL_EFFECT=100
    WHEN_EFFECT=101
    ASSIGN_EFFECT=102
    NOT_EFFECT=103
    PRED_HEAD=104
    GOAL=105
    BINARY_OP=106
    UNARY_MINUS=107
    INIT_EQ=108
    INIT_AT=109
    NOT_PRED_INIT=110
    PRED_INST=111
    PROBLEM_CONSTRAINT=112
    PROBLEM_METRIC=113

    def __init__(self, input:TokenStream):
        super().__init__(input)
        self.checkVersion("4.5")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None



    class PddlDocContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def domain(self):
            return self.getTypedRuleContext(pddlParser.DomainContext,0)


        def problem(self):
            return self.getTypedRuleContext(pddlParser.ProblemContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_pddlDoc

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterPddlDoc(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitPddlDoc(self)




    def pddlDoc(self):

        localctx = pddlParser.PddlDocContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_pddlDoc)
        try:
            self.state = 144
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 142
                self.domain()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 143
                self.problem()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DomainContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def domainName(self):
            return self.getTypedRuleContext(pddlParser.DomainNameContext,0)


        def requireDef(self):
            return self.getTypedRuleContext(pddlParser.RequireDefContext,0)


        def typesDef(self):
            return self.getTypedRuleContext(pddlParser.TypesDefContext,0)


        def constantsDef(self):
            return self.getTypedRuleContext(pddlParser.ConstantsDefContext,0)


        def predicatesDef(self):
            return self.getTypedRuleContext(pddlParser.PredicatesDefContext,0)


        def functionsDef(self):
            return self.getTypedRuleContext(pddlParser.FunctionsDefContext,0)


        def constraints(self):
            return self.getTypedRuleContext(pddlParser.ConstraintsContext,0)


        def structureDef(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.StructureDefContext)
            else:
                return self.getTypedRuleContext(pddlParser.StructureDefContext,i)


        def getRuleIndex(self):
            return pddlParser.RULE_domain

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterDomain(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitDomain(self)




    def domain(self):

        localctx = pddlParser.DomainContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_domain)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 146
            self.match(pddlParser.T__0)
            self.state = 147
            self.match(pddlParser.T__1)
            self.state = 148
            self.domainName()
            self.state = 150
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.state = 149
                self.requireDef()


            self.state = 153
            la_ = self._interp.adaptivePredict(self._input,2,self._ctx)
            if la_ == 1:
                self.state = 152
                self.typesDef()


            self.state = 156
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.state = 155
                self.constantsDef()


            self.state = 159
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.state = 158
                self.predicatesDef()


            self.state = 162
            la_ = self._interp.adaptivePredict(self._input,5,self._ctx)
            if la_ == 1:
                self.state = 161
                self.functionsDef()


            self.state = 165
            la_ = self._interp.adaptivePredict(self._input,6,self._ctx)
            if la_ == 1:
                self.state = 164
                self.constraints()


            self.state = 170
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pddlParser.T__0:
                self.state = 167
                self.structureDef()
                self.state = 172
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 173
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DomainNameContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self):
            return self.getToken(pddlParser.NAME, 0)

        def getRuleIndex(self):
            return pddlParser.RULE_domainName

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterDomainName(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitDomainName(self)




    def domainName(self):

        localctx = pddlParser.DomainNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_domainName)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 175
            self.match(pddlParser.T__0)
            self.state = 176
            self.match(pddlParser.T__3)
            self.state = 177
            self.match(pddlParser.NAME)
            self.state = 178
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class RequireDefContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def REQUIRE_KEY(self, i:int=None):
            if i is None:
                return self.getTokens(pddlParser.REQUIRE_KEY)
            else:
                return self.getToken(pddlParser.REQUIRE_KEY, i)

        def getRuleIndex(self):
            return pddlParser.RULE_requireDef

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterRequireDef(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitRequireDef(self)




    def requireDef(self):

        localctx = pddlParser.RequireDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_requireDef)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 180
            self.match(pddlParser.T__0)
            self.state = 181
            self.match(pddlParser.T__4)
            self.state = 183 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 182
                self.match(pddlParser.REQUIRE_KEY)
                self.state = 185 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==pddlParser.REQUIRE_KEY):
                    break

            self.state = 187
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class TypesDefContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def typedNameList(self):
            return self.getTypedRuleContext(pddlParser.TypedNameListContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_typesDef

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterTypesDef(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitTypesDef(self)




    def typesDef(self):

        localctx = pddlParser.TypesDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_typesDef)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 189
            self.match(pddlParser.T__0)
            self.state = 190
            self.match(pddlParser.T__5)
            self.state = 191
            self.typedNameList()
            self.state = 192
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class TypedNameListContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self, i:int=None):
            if i is None:
                return self.getTokens(pddlParser.NAME)
            else:
                return self.getToken(pddlParser.NAME, i)

        def singleTypeNameList(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.SingleTypeNameListContext)
            else:
                return self.getTypedRuleContext(pddlParser.SingleTypeNameListContext,i)


        def getRuleIndex(self):
            return pddlParser.RULE_typedNameList

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterTypedNameList(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitTypedNameList(self)




    def typedNameList(self):

        localctx = pddlParser.TypedNameListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_typedNameList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 211
            la_ = self._interp.adaptivePredict(self._input,12,self._ctx)
            if la_ == 1:
                self.state = 197
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==pddlParser.NAME:
                    self.state = 194
                    self.match(pddlParser.NAME)
                    self.state = 199
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 2:
                self.state = 201 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 200
                        self.singleTypeNameList()

                    else:
                        raise NoViableAltException(self)
                    self.state = 203 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,10,self._ctx)

                self.state = 208
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==pddlParser.NAME:
                    self.state = 205
                    self.match(pddlParser.NAME)
                    self.state = 210
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class SingleTypeNameListContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.t = None # R_typeContext

        def r_type(self):
            return self.getTypedRuleContext(pddlParser.R_typeContext,0)


        def NAME(self, i:int=None):
            if i is None:
                return self.getTokens(pddlParser.NAME)
            else:
                return self.getToken(pddlParser.NAME, i)

        def getRuleIndex(self):
            return pddlParser.RULE_singleTypeNameList

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterSingleTypeNameList(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitSingleTypeNameList(self)




    def singleTypeNameList(self):

        localctx = pddlParser.SingleTypeNameListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_singleTypeNameList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 214 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 213
                self.match(pddlParser.NAME)
                self.state = 216 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==pddlParser.NAME):
                    break

            self.state = 218
            self.match(pddlParser.T__6)
            self.state = 219
            localctx.t = self.r_type()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class R_typeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def primType(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.PrimTypeContext)
            else:
                return self.getTypedRuleContext(pddlParser.PrimTypeContext,i)


        def getRuleIndex(self):
            return pddlParser.RULE_r_type

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterR_type(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitR_type(self)




    def r_type(self):

        localctx = pddlParser.R_typeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_r_type)
        self._la = 0 # Token type
        try:
            self.state = 231
            token = self._input.LA(1)
            if token in [pddlParser.T__0]:
                self.enterOuterAlt(localctx, 1)
                self.state = 221
                self.match(pddlParser.T__0)
                self.state = 222
                self.match(pddlParser.T__7)
                self.state = 224 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 223
                    self.primType()
                    self.state = 226 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==pddlParser.NAME):
                        break

                self.state = 228
                self.match(pddlParser.T__2)

            elif token in [pddlParser.NAME]:
                self.enterOuterAlt(localctx, 2)
                self.state = 230
                self.primType()

            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PrimTypeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self):
            return self.getToken(pddlParser.NAME, 0)

        def getRuleIndex(self):
            return pddlParser.RULE_primType

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterPrimType(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitPrimType(self)




    def primType(self):

        localctx = pddlParser.PrimTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_primType)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 233
            self.match(pddlParser.NAME)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FunctionsDefContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def functionList(self):
            return self.getTypedRuleContext(pddlParser.FunctionListContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_functionsDef

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterFunctionsDef(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitFunctionsDef(self)




    def functionsDef(self):

        localctx = pddlParser.FunctionsDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_functionsDef)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 235
            self.match(pddlParser.T__0)
            self.state = 236
            self.match(pddlParser.T__8)
            self.state = 237
            self.functionList()
            self.state = 238
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FunctionListContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def atomicFunctionSkeleton(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.AtomicFunctionSkeletonContext)
            else:
                return self.getTypedRuleContext(pddlParser.AtomicFunctionSkeletonContext,i)


        def functionType(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.FunctionTypeContext)
            else:
                return self.getTypedRuleContext(pddlParser.FunctionTypeContext,i)


        def getRuleIndex(self):
            return pddlParser.RULE_functionList

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterFunctionList(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitFunctionList(self)




    def functionList(self):

        localctx = pddlParser.FunctionListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_functionList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 251
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pddlParser.T__0:
                self.state = 241 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 240
                        self.atomicFunctionSkeleton()

                    else:
                        raise NoViableAltException(self)
                    self.state = 243 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,16,self._ctx)

                self.state = 247
                _la = self._input.LA(1)
                if _la==pddlParser.T__6:
                    self.state = 245
                    self.match(pddlParser.T__6)
                    self.state = 246
                    self.functionType()


                self.state = 253
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class AtomicFunctionSkeletonContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def functionSymbol(self):
            return self.getTypedRuleContext(pddlParser.FunctionSymbolContext,0)


        def typedVariableList(self):
            return self.getTypedRuleContext(pddlParser.TypedVariableListContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_atomicFunctionSkeleton

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterAtomicFunctionSkeleton(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitAtomicFunctionSkeleton(self)




    def atomicFunctionSkeleton(self):

        localctx = pddlParser.AtomicFunctionSkeletonContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_atomicFunctionSkeleton)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 254
            self.match(pddlParser.T__0)
            self.state = 255
            self.functionSymbol()
            self.state = 256
            self.typedVariableList()
            self.state = 257
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FunctionSymbolContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self):
            return self.getToken(pddlParser.NAME, 0)

        def getRuleIndex(self):
            return pddlParser.RULE_functionSymbol

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterFunctionSymbol(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitFunctionSymbol(self)




    def functionSymbol(self):

        localctx = pddlParser.FunctionSymbolContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_functionSymbol)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 259
            self.match(pddlParser.NAME)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FunctionTypeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return pddlParser.RULE_functionType

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterFunctionType(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitFunctionType(self)




    def functionType(self):

        localctx = pddlParser.FunctionTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_functionType)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 261
            self.match(pddlParser.T__9)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ConstantsDefContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def typedNameList(self):
            return self.getTypedRuleContext(pddlParser.TypedNameListContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_constantsDef

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterConstantsDef(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitConstantsDef(self)




    def constantsDef(self):

        localctx = pddlParser.ConstantsDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_constantsDef)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 263
            self.match(pddlParser.T__0)
            self.state = 264
            self.match(pddlParser.T__10)
            self.state = 265
            self.typedNameList()
            self.state = 266
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PredicatesDefContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def atomicFormulaSkeleton(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.AtomicFormulaSkeletonContext)
            else:
                return self.getTypedRuleContext(pddlParser.AtomicFormulaSkeletonContext,i)


        def getRuleIndex(self):
            return pddlParser.RULE_predicatesDef

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterPredicatesDef(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitPredicatesDef(self)




    def predicatesDef(self):

        localctx = pddlParser.PredicatesDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_predicatesDef)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 268
            self.match(pddlParser.T__0)
            self.state = 269
            self.match(pddlParser.T__11)
            self.state = 271 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 270
                self.atomicFormulaSkeleton()
                self.state = 273 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==pddlParser.T__0):
                    break

            self.state = 275
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class AtomicFormulaSkeletonContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def predicate(self):
            return self.getTypedRuleContext(pddlParser.PredicateContext,0)


        def typedVariableList(self):
            return self.getTypedRuleContext(pddlParser.TypedVariableListContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_atomicFormulaSkeleton

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterAtomicFormulaSkeleton(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitAtomicFormulaSkeleton(self)




    def atomicFormulaSkeleton(self):

        localctx = pddlParser.AtomicFormulaSkeletonContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_atomicFormulaSkeleton)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 277
            self.match(pddlParser.T__0)
            self.state = 278
            self.predicate()
            self.state = 279
            self.typedVariableList()
            self.state = 280
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PredicateContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self):
            return self.getToken(pddlParser.NAME, 0)

        def getRuleIndex(self):
            return pddlParser.RULE_predicate

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterPredicate(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitPredicate(self)




    def predicate(self):

        localctx = pddlParser.PredicateContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_predicate)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 282
            self.match(pddlParser.NAME)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class TypedVariableListContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def VARIABLE(self, i:int=None):
            if i is None:
                return self.getTokens(pddlParser.VARIABLE)
            else:
                return self.getToken(pddlParser.VARIABLE, i)

        def singleTypeVarList(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.SingleTypeVarListContext)
            else:
                return self.getTypedRuleContext(pddlParser.SingleTypeVarListContext,i)


        def getRuleIndex(self):
            return pddlParser.RULE_typedVariableList

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterTypedVariableList(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitTypedVariableList(self)




    def typedVariableList(self):

        localctx = pddlParser.TypedVariableListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_typedVariableList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 301
            la_ = self._interp.adaptivePredict(self._input,23,self._ctx)
            if la_ == 1:
                self.state = 287
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==pddlParser.VARIABLE:
                    self.state = 284
                    self.match(pddlParser.VARIABLE)
                    self.state = 289
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 2:
                self.state = 291 
                self._errHandler.sync(self)
                _alt = 1
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt == 1:
                        self.state = 290
                        self.singleTypeVarList()

                    else:
                        raise NoViableAltException(self)
                    self.state = 293 
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,21,self._ctx)

                self.state = 298
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==pddlParser.VARIABLE:
                    self.state = 295
                    self.match(pddlParser.VARIABLE)
                    self.state = 300
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class SingleTypeVarListContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.t = None # R_typeContext

        def r_type(self):
            return self.getTypedRuleContext(pddlParser.R_typeContext,0)


        def VARIABLE(self, i:int=None):
            if i is None:
                return self.getTokens(pddlParser.VARIABLE)
            else:
                return self.getToken(pddlParser.VARIABLE, i)

        def getRuleIndex(self):
            return pddlParser.RULE_singleTypeVarList

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterSingleTypeVarList(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitSingleTypeVarList(self)




    def singleTypeVarList(self):

        localctx = pddlParser.SingleTypeVarListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_singleTypeVarList)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 304 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 303
                self.match(pddlParser.VARIABLE)
                self.state = 306 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==pddlParser.VARIABLE):
                    break

            self.state = 308
            self.match(pddlParser.T__6)
            self.state = 309
            localctx.t = self.r_type()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ConstraintsContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def conGD(self):
            return self.getTypedRuleContext(pddlParser.ConGDContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_constraints

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterConstraints(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitConstraints(self)




    def constraints(self):

        localctx = pddlParser.ConstraintsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_constraints)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 311
            self.match(pddlParser.T__0)
            self.state = 312
            self.match(pddlParser.T__12)
            self.state = 313
            self.conGD()
            self.state = 314
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class StructureDefContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def actionDef(self):
            return self.getTypedRuleContext(pddlParser.ActionDefContext,0)


        def durativeActionDef(self):
            return self.getTypedRuleContext(pddlParser.DurativeActionDefContext,0)


        def derivedDef(self):
            return self.getTypedRuleContext(pddlParser.DerivedDefContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_structureDef

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterStructureDef(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitStructureDef(self)




    def structureDef(self):

        localctx = pddlParser.StructureDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_structureDef)
        try:
            self.state = 319
            la_ = self._interp.adaptivePredict(self._input,25,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 316
                self.actionDef()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 317
                self.durativeActionDef()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 318
                self.derivedDef()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ActionDefContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def actionSymbol(self):
            return self.getTypedRuleContext(pddlParser.ActionSymbolContext,0)


        def typedVariableList(self):
            return self.getTypedRuleContext(pddlParser.TypedVariableListContext,0)


        def actionDefBody(self):
            return self.getTypedRuleContext(pddlParser.ActionDefBodyContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_actionDef

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterActionDef(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitActionDef(self)




    def actionDef(self):

        localctx = pddlParser.ActionDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_actionDef)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 321
            self.match(pddlParser.T__0)
            self.state = 322
            self.match(pddlParser.T__13)
            self.state = 323
            self.actionSymbol()
            self.state = 324
            self.match(pddlParser.T__14)
            self.state = 325
            self.match(pddlParser.T__0)
            self.state = 326
            self.typedVariableList()
            self.state = 327
            self.match(pddlParser.T__2)
            self.state = 328
            self.actionDefBody()
            self.state = 329
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ActionSymbolContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self):
            return self.getToken(pddlParser.NAME, 0)

        def getRuleIndex(self):
            return pddlParser.RULE_actionSymbol

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterActionSymbol(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitActionSymbol(self)




    def actionSymbol(self):

        localctx = pddlParser.ActionSymbolContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_actionSymbol)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 331
            self.match(pddlParser.NAME)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ActionDefBodyContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def precondition(self):
            return self.getTypedRuleContext(pddlParser.PreconditionContext,0)


        def effect(self):
            return self.getTypedRuleContext(pddlParser.EffectContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_actionDefBody

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterActionDefBody(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitActionDefBody(self)




    def actionDefBody(self):

        localctx = pddlParser.ActionDefBodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_actionDefBody)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 339
            _la = self._input.LA(1)
            if _la==pddlParser.T__15:
                self.state = 333
                self.match(pddlParser.T__15)
                self.state = 337
                la_ = self._interp.adaptivePredict(self._input,26,self._ctx)
                if la_ == 1:
                    self.state = 334
                    self.match(pddlParser.T__0)
                    self.state = 335
                    self.match(pddlParser.T__2)
                    pass

                elif la_ == 2:
                    self.state = 336
                    self.precondition()
                    pass




            self.state = 347
            _la = self._input.LA(1)
            if _la==pddlParser.T__16:
                self.state = 341
                self.match(pddlParser.T__16)
                self.state = 345
                la_ = self._interp.adaptivePredict(self._input,28,self._ctx)
                if la_ == 1:
                    self.state = 342
                    self.match(pddlParser.T__0)
                    self.state = 343
                    self.match(pddlParser.T__2)
                    pass

                elif la_ == 2:
                    self.state = 344
                    self.effect()
                    pass




        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PreconditionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def goalDesc(self):
            return self.getTypedRuleContext(pddlParser.GoalDescContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_precondition

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterPrecondition(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitPrecondition(self)




    def precondition(self):

        localctx = pddlParser.PreconditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_precondition)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 349
            self.goalDesc()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class GoalDescContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def atomicTermFormula(self):
            return self.getTypedRuleContext(pddlParser.AtomicTermFormulaContext,0)


        def goalDesc(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.GoalDescContext)
            else:
                return self.getTypedRuleContext(pddlParser.GoalDescContext,i)


        def typedVariableList(self):
            return self.getTypedRuleContext(pddlParser.TypedVariableListContext,0)


        def fComp(self):
            return self.getTypedRuleContext(pddlParser.FCompContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_goalDesc

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterGoalDesc(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitGoalDesc(self)




    def goalDesc(self):

        localctx = pddlParser.GoalDescContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_goalDesc)
        self._la = 0 # Token type
        try:
            self.state = 398
            la_ = self._interp.adaptivePredict(self._input,32,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 351
                self.atomicTermFormula()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 352
                self.match(pddlParser.T__0)
                self.state = 353
                self.match(pddlParser.T__17)
                self.state = 357
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==pddlParser.T__0:
                    self.state = 354
                    self.goalDesc()
                    self.state = 359
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 360
                self.match(pddlParser.T__2)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 361
                self.match(pddlParser.T__0)
                self.state = 362
                self.match(pddlParser.T__18)
                self.state = 366
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==pddlParser.T__0:
                    self.state = 363
                    self.goalDesc()
                    self.state = 368
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 369
                self.match(pddlParser.T__2)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 370
                self.match(pddlParser.T__0)
                self.state = 371
                self.match(pddlParser.T__19)
                self.state = 372
                self.goalDesc()
                self.state = 373
                self.match(pddlParser.T__2)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 375
                self.match(pddlParser.T__0)
                self.state = 376
                self.match(pddlParser.T__20)
                self.state = 377
                self.goalDesc()
                self.state = 378
                self.goalDesc()
                self.state = 379
                self.match(pddlParser.T__2)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 381
                self.match(pddlParser.T__0)
                self.state = 382
                self.match(pddlParser.T__21)
                self.state = 383
                self.match(pddlParser.T__0)
                self.state = 384
                self.typedVariableList()
                self.state = 385
                self.match(pddlParser.T__2)
                self.state = 386
                self.goalDesc()
                self.state = 387
                self.match(pddlParser.T__2)
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 389
                self.match(pddlParser.T__0)
                self.state = 390
                self.match(pddlParser.T__22)
                self.state = 391
                self.match(pddlParser.T__0)
                self.state = 392
                self.typedVariableList()
                self.state = 393
                self.match(pddlParser.T__2)
                self.state = 394
                self.goalDesc()
                self.state = 395
                self.match(pddlParser.T__2)
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 397
                self.fComp()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FCompContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def binaryComp(self):
            return self.getTypedRuleContext(pddlParser.BinaryCompContext,0)


        def fExp(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.FExpContext)
            else:
                return self.getTypedRuleContext(pddlParser.FExpContext,i)


        def getRuleIndex(self):
            return pddlParser.RULE_fComp

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterFComp(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitFComp(self)




    def fComp(self):

        localctx = pddlParser.FCompContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_fComp)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 400
            self.match(pddlParser.T__0)
            self.state = 401
            self.binaryComp()
            self.state = 402
            self.fExp()
            self.state = 403
            self.fExp()
            self.state = 404
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class AtomicTermFormulaContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def predicate(self):
            return self.getTypedRuleContext(pddlParser.PredicateContext,0)


        def term(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.TermContext)
            else:
                return self.getTypedRuleContext(pddlParser.TermContext,i)


        def getRuleIndex(self):
            return pddlParser.RULE_atomicTermFormula

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterAtomicTermFormula(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitAtomicTermFormula(self)




    def atomicTermFormula(self):

        localctx = pddlParser.AtomicTermFormulaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_atomicTermFormula)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 406
            self.match(pddlParser.T__0)
            self.state = 407
            self.predicate()
            self.state = 411
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pddlParser.NAME or _la==pddlParser.VARIABLE:
                self.state = 408
                self.term()
                self.state = 413
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 414
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class TermContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self):
            return self.getToken(pddlParser.NAME, 0)

        def VARIABLE(self):
            return self.getToken(pddlParser.VARIABLE, 0)

        def getRuleIndex(self):
            return pddlParser.RULE_term

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterTerm(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitTerm(self)




    def term(self):

        localctx = pddlParser.TermContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_term)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 416
            _la = self._input.LA(1)
            if not(_la==pddlParser.NAME or _la==pddlParser.VARIABLE):
                self._errHandler.recoverInline(self)
            else:
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DurativeActionDefContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def actionSymbol(self):
            return self.getTypedRuleContext(pddlParser.ActionSymbolContext,0)


        def typedVariableList(self):
            return self.getTypedRuleContext(pddlParser.TypedVariableListContext,0)


        def daDefBody(self):
            return self.getTypedRuleContext(pddlParser.DaDefBodyContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_durativeActionDef

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterDurativeActionDef(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitDurativeActionDef(self)




    def durativeActionDef(self):

        localctx = pddlParser.DurativeActionDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_durativeActionDef)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 418
            self.match(pddlParser.T__0)
            self.state = 419
            self.match(pddlParser.T__23)
            self.state = 420
            self.actionSymbol()
            self.state = 421
            self.match(pddlParser.T__14)
            self.state = 422
            self.match(pddlParser.T__0)
            self.state = 423
            self.typedVariableList()
            self.state = 424
            self.match(pddlParser.T__2)
            self.state = 425
            self.daDefBody()
            self.state = 426
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DaDefBodyContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def durationConstraint(self):
            return self.getTypedRuleContext(pddlParser.DurationConstraintContext,0)


        def daGD(self):
            return self.getTypedRuleContext(pddlParser.DaGDContext,0)


        def daEffect(self):
            return self.getTypedRuleContext(pddlParser.DaEffectContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_daDefBody

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterDaDefBody(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitDaDefBody(self)




    def daDefBody(self):

        localctx = pddlParser.DaDefBodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_daDefBody)
        try:
            self.state = 442
            token = self._input.LA(1)
            if token in [pddlParser.T__24]:
                self.enterOuterAlt(localctx, 1)
                self.state = 428
                self.match(pddlParser.T__24)
                self.state = 429
                self.durationConstraint()

            elif token in [pddlParser.T__25]:
                self.enterOuterAlt(localctx, 2)
                self.state = 430
                self.match(pddlParser.T__25)
                self.state = 434
                la_ = self._interp.adaptivePredict(self._input,34,self._ctx)
                if la_ == 1:
                    self.state = 431
                    self.match(pddlParser.T__0)
                    self.state = 432
                    self.match(pddlParser.T__2)
                    pass

                elif la_ == 2:
                    self.state = 433
                    self.daGD()
                    pass



            elif token in [pddlParser.T__16]:
                self.enterOuterAlt(localctx, 3)
                self.state = 436
                self.match(pddlParser.T__16)
                self.state = 440
                la_ = self._interp.adaptivePredict(self._input,35,self._ctx)
                if la_ == 1:
                    self.state = 437
                    self.match(pddlParser.T__0)
                    self.state = 438
                    self.match(pddlParser.T__2)
                    pass

                elif la_ == 2:
                    self.state = 439
                    self.daEffect()
                    pass



            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DaGDContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def prefTimedGD(self):
            return self.getTypedRuleContext(pddlParser.PrefTimedGDContext,0)


        def daGD(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.DaGDContext)
            else:
                return self.getTypedRuleContext(pddlParser.DaGDContext,i)


        def typedVariableList(self):
            return self.getTypedRuleContext(pddlParser.TypedVariableListContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_daGD

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterDaGD(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitDaGD(self)




    def daGD(self):

        localctx = pddlParser.DaGDContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_daGD)
        self._la = 0 # Token type
        try:
            self.state = 462
            la_ = self._interp.adaptivePredict(self._input,38,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 444
                self.prefTimedGD()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 445
                self.match(pddlParser.T__0)
                self.state = 446
                self.match(pddlParser.T__17)
                self.state = 450
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==pddlParser.T__0:
                    self.state = 447
                    self.daGD()
                    self.state = 452
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 453
                self.match(pddlParser.T__2)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 454
                self.match(pddlParser.T__0)
                self.state = 455
                self.match(pddlParser.T__22)
                self.state = 456
                self.match(pddlParser.T__0)
                self.state = 457
                self.typedVariableList()
                self.state = 458
                self.match(pddlParser.T__2)
                self.state = 459
                self.daGD()
                self.state = 460
                self.match(pddlParser.T__2)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PrefTimedGDContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def timedGD(self):
            return self.getTypedRuleContext(pddlParser.TimedGDContext,0)


        def NAME(self):
            return self.getToken(pddlParser.NAME, 0)

        def getRuleIndex(self):
            return pddlParser.RULE_prefTimedGD

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterPrefTimedGD(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitPrefTimedGD(self)




    def prefTimedGD(self):

        localctx = pddlParser.PrefTimedGDContext(self, self._ctx, self.state)
        self.enterRule(localctx, 66, self.RULE_prefTimedGD)
        self._la = 0 # Token type
        try:
            self.state = 473
            la_ = self._interp.adaptivePredict(self._input,40,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 464
                self.timedGD()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 465
                self.match(pddlParser.T__0)
                self.state = 466
                self.match(pddlParser.T__26)
                self.state = 468
                _la = self._input.LA(1)
                if _la==pddlParser.NAME:
                    self.state = 467
                    self.match(pddlParser.NAME)


                self.state = 470
                self.timedGD()
                self.state = 471
                self.match(pddlParser.T__2)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class TimedGDContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def timeSpecifier(self):
            return self.getTypedRuleContext(pddlParser.TimeSpecifierContext,0)


        def goalDesc(self):
            return self.getTypedRuleContext(pddlParser.GoalDescContext,0)


        def interval(self):
            return self.getTypedRuleContext(pddlParser.IntervalContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_timedGD

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterTimedGD(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitTimedGD(self)




    def timedGD(self):

        localctx = pddlParser.TimedGDContext(self, self._ctx, self.state)
        self.enterRule(localctx, 68, self.RULE_timedGD)
        try:
            self.state = 487
            la_ = self._interp.adaptivePredict(self._input,41,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 475
                self.match(pddlParser.T__0)
                self.state = 476
                self.match(pddlParser.T__27)
                self.state = 477
                self.timeSpecifier()
                self.state = 478
                self.goalDesc()
                self.state = 479
                self.match(pddlParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 481
                self.match(pddlParser.T__0)
                self.state = 482
                self.match(pddlParser.T__28)
                self.state = 483
                self.interval()
                self.state = 484
                self.goalDesc()
                self.state = 485
                self.match(pddlParser.T__2)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class TimeSpecifierContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return pddlParser.RULE_timeSpecifier

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterTimeSpecifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitTimeSpecifier(self)




    def timeSpecifier(self):

        localctx = pddlParser.TimeSpecifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 70, self.RULE_timeSpecifier)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 489
            _la = self._input.LA(1)
            if not(_la==pddlParser.T__29 or _la==pddlParser.T__30):
                self._errHandler.recoverInline(self)
            else:
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class IntervalContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return pddlParser.RULE_interval

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterInterval(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitInterval(self)




    def interval(self):

        localctx = pddlParser.IntervalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 72, self.RULE_interval)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 491
            self.match(pddlParser.T__31)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DerivedDefContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def typedVariableList(self):
            return self.getTypedRuleContext(pddlParser.TypedVariableListContext,0)


        def goalDesc(self):
            return self.getTypedRuleContext(pddlParser.GoalDescContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_derivedDef

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterDerivedDef(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitDerivedDef(self)




    def derivedDef(self):

        localctx = pddlParser.DerivedDefContext(self, self._ctx, self.state)
        self.enterRule(localctx, 74, self.RULE_derivedDef)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 493
            self.match(pddlParser.T__0)
            self.state = 494
            self.match(pddlParser.T__32)
            self.state = 495
            self.typedVariableList()
            self.state = 496
            self.goalDesc()
            self.state = 497
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FExpContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(pddlParser.NUMBER, 0)

        def binaryOp(self):
            return self.getTypedRuleContext(pddlParser.BinaryOpContext,0)


        def fExp(self):
            return self.getTypedRuleContext(pddlParser.FExpContext,0)


        def fExp2(self):
            return self.getTypedRuleContext(pddlParser.FExp2Context,0)


        def fHead(self):
            return self.getTypedRuleContext(pddlParser.FHeadContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_fExp

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterFExp(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitFExp(self)




    def fExp(self):

        localctx = pddlParser.FExpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 76, self.RULE_fExp)
        try:
            self.state = 512
            la_ = self._interp.adaptivePredict(self._input,42,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 499
                self.match(pddlParser.NUMBER)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 500
                self.match(pddlParser.T__0)
                self.state = 501
                self.binaryOp()
                self.state = 502
                self.fExp()
                self.state = 503
                self.fExp2()
                self.state = 504
                self.match(pddlParser.T__2)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 506
                self.match(pddlParser.T__0)
                self.state = 507
                self.match(pddlParser.T__6)
                self.state = 508
                self.fExp()
                self.state = 509
                self.match(pddlParser.T__2)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 511
                self.fHead()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FExp2Context(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def fExp(self):
            return self.getTypedRuleContext(pddlParser.FExpContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_fExp2

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterFExp2(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitFExp2(self)




    def fExp2(self):

        localctx = pddlParser.FExp2Context(self, self._ctx, self.state)
        self.enterRule(localctx, 78, self.RULE_fExp2)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 514
            self.fExp()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FHeadContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def functionSymbol(self):
            return self.getTypedRuleContext(pddlParser.FunctionSymbolContext,0)


        def term(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.TermContext)
            else:
                return self.getTypedRuleContext(pddlParser.TermContext,i)


        def getRuleIndex(self):
            return pddlParser.RULE_fHead

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterFHead(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitFHead(self)




    def fHead(self):

        localctx = pddlParser.FHeadContext(self, self._ctx, self.state)
        self.enterRule(localctx, 80, self.RULE_fHead)
        self._la = 0 # Token type
        try:
            self.state = 527
            token = self._input.LA(1)
            if token in [pddlParser.T__0]:
                self.enterOuterAlt(localctx, 1)
                self.state = 516
                self.match(pddlParser.T__0)
                self.state = 517
                self.functionSymbol()
                self.state = 521
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==pddlParser.NAME or _la==pddlParser.VARIABLE:
                    self.state = 518
                    self.term()
                    self.state = 523
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 524
                self.match(pddlParser.T__2)

            elif token in [pddlParser.NAME]:
                self.enterOuterAlt(localctx, 2)
                self.state = 526
                self.functionSymbol()

            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class EffectContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def cEffect(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.CEffectContext)
            else:
                return self.getTypedRuleContext(pddlParser.CEffectContext,i)


        def getRuleIndex(self):
            return pddlParser.RULE_effect

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterEffect(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitEffect(self)




    def effect(self):

        localctx = pddlParser.EffectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 82, self.RULE_effect)
        self._la = 0 # Token type
        try:
            self.state = 539
            la_ = self._interp.adaptivePredict(self._input,46,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 529
                self.match(pddlParser.T__0)
                self.state = 530
                self.match(pddlParser.T__17)
                self.state = 534
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==pddlParser.T__0:
                    self.state = 531
                    self.cEffect()
                    self.state = 536
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 537
                self.match(pddlParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 538
                self.cEffect()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class CEffectContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def typedVariableList(self):
            return self.getTypedRuleContext(pddlParser.TypedVariableListContext,0)


        def effect(self):
            return self.getTypedRuleContext(pddlParser.EffectContext,0)


        def goalDesc(self):
            return self.getTypedRuleContext(pddlParser.GoalDescContext,0)


        def condEffect(self):
            return self.getTypedRuleContext(pddlParser.CondEffectContext,0)


        def pEffect(self):
            return self.getTypedRuleContext(pddlParser.PEffectContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_cEffect

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterCEffect(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitCEffect(self)




    def cEffect(self):

        localctx = pddlParser.CEffectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 84, self.RULE_cEffect)
        try:
            self.state = 556
            la_ = self._interp.adaptivePredict(self._input,47,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 541
                self.match(pddlParser.T__0)
                self.state = 542
                self.match(pddlParser.T__22)
                self.state = 543
                self.match(pddlParser.T__0)
                self.state = 544
                self.typedVariableList()
                self.state = 545
                self.match(pddlParser.T__2)
                self.state = 546
                self.effect()
                self.state = 547
                self.match(pddlParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 549
                self.match(pddlParser.T__0)
                self.state = 550
                self.match(pddlParser.T__33)
                self.state = 551
                self.goalDesc()
                self.state = 552
                self.condEffect()
                self.state = 553
                self.match(pddlParser.T__2)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 555
                self.pEffect()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PEffectContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def assignOp(self):
            return self.getTypedRuleContext(pddlParser.AssignOpContext,0)


        def fHead(self):
            return self.getTypedRuleContext(pddlParser.FHeadContext,0)


        def fExp(self):
            return self.getTypedRuleContext(pddlParser.FExpContext,0)


        def atomicTermFormula(self):
            return self.getTypedRuleContext(pddlParser.AtomicTermFormulaContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_pEffect

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterPEffect(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitPEffect(self)




    def pEffect(self):

        localctx = pddlParser.PEffectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 86, self.RULE_pEffect)
        try:
            self.state = 570
            la_ = self._interp.adaptivePredict(self._input,48,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 558
                self.match(pddlParser.T__0)
                self.state = 559
                self.assignOp()
                self.state = 560
                self.fHead()
                self.state = 561
                self.fExp()
                self.state = 562
                self.match(pddlParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 564
                self.match(pddlParser.T__0)
                self.state = 565
                self.match(pddlParser.T__19)
                self.state = 566
                self.atomicTermFormula()
                self.state = 567
                self.match(pddlParser.T__2)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 569
                self.atomicTermFormula()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class CondEffectContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def pEffect(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.PEffectContext)
            else:
                return self.getTypedRuleContext(pddlParser.PEffectContext,i)


        def getRuleIndex(self):
            return pddlParser.RULE_condEffect

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterCondEffect(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitCondEffect(self)




    def condEffect(self):

        localctx = pddlParser.CondEffectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 88, self.RULE_condEffect)
        self._la = 0 # Token type
        try:
            self.state = 582
            la_ = self._interp.adaptivePredict(self._input,50,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 572
                self.match(pddlParser.T__0)
                self.state = 573
                self.match(pddlParser.T__17)
                self.state = 577
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==pddlParser.T__0:
                    self.state = 574
                    self.pEffect()
                    self.state = 579
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 580
                self.match(pddlParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 581
                self.pEffect()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class BinaryOpContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return pddlParser.RULE_binaryOp

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterBinaryOp(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitBinaryOp(self)




    def binaryOp(self):

        localctx = pddlParser.BinaryOpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 90, self.RULE_binaryOp)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 584
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << pddlParser.T__6) | (1 << pddlParser.T__34) | (1 << pddlParser.T__35) | (1 << pddlParser.T__36))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class BinaryCompContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return pddlParser.RULE_binaryComp

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterBinaryComp(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitBinaryComp(self)




    def binaryComp(self):

        localctx = pddlParser.BinaryCompContext(self, self._ctx, self.state)
        self.enterRule(localctx, 92, self.RULE_binaryComp)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 586
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << pddlParser.T__37) | (1 << pddlParser.T__38) | (1 << pddlParser.T__39) | (1 << pddlParser.T__40) | (1 << pddlParser.T__41))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class AssignOpContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return pddlParser.RULE_assignOp

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterAssignOp(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitAssignOp(self)




    def assignOp(self):

        localctx = pddlParser.AssignOpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 94, self.RULE_assignOp)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 588
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << pddlParser.T__42) | (1 << pddlParser.T__43) | (1 << pddlParser.T__44) | (1 << pddlParser.T__45) | (1 << pddlParser.T__46))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DurationConstraintContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def simpleDurationConstraint(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.SimpleDurationConstraintContext)
            else:
                return self.getTypedRuleContext(pddlParser.SimpleDurationConstraintContext,i)


        def getRuleIndex(self):
            return pddlParser.RULE_durationConstraint

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterDurationConstraint(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitDurationConstraint(self)




    def durationConstraint(self):

        localctx = pddlParser.DurationConstraintContext(self, self._ctx, self.state)
        self.enterRule(localctx, 96, self.RULE_durationConstraint)
        self._la = 0 # Token type
        try:
            self.state = 602
            la_ = self._interp.adaptivePredict(self._input,52,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 590
                self.match(pddlParser.T__0)
                self.state = 591
                self.match(pddlParser.T__17)
                self.state = 593 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 592
                    self.simpleDurationConstraint()
                    self.state = 595 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==pddlParser.T__0):
                        break

                self.state = 597
                self.match(pddlParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 599
                self.match(pddlParser.T__0)
                self.state = 600
                self.match(pddlParser.T__2)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 601
                self.simpleDurationConstraint()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class SimpleDurationConstraintContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def durOp(self):
            return self.getTypedRuleContext(pddlParser.DurOpContext,0)


        def durValue(self):
            return self.getTypedRuleContext(pddlParser.DurValueContext,0)


        def timeSpecifier(self):
            return self.getTypedRuleContext(pddlParser.TimeSpecifierContext,0)


        def simpleDurationConstraint(self):
            return self.getTypedRuleContext(pddlParser.SimpleDurationConstraintContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_simpleDurationConstraint

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterSimpleDurationConstraint(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitSimpleDurationConstraint(self)




    def simpleDurationConstraint(self):

        localctx = pddlParser.SimpleDurationConstraintContext(self, self._ctx, self.state)
        self.enterRule(localctx, 98, self.RULE_simpleDurationConstraint)
        try:
            self.state = 616
            la_ = self._interp.adaptivePredict(self._input,53,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 604
                self.match(pddlParser.T__0)
                self.state = 605
                self.durOp()
                self.state = 606
                self.match(pddlParser.T__47)
                self.state = 607
                self.durValue()
                self.state = 608
                self.match(pddlParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 610
                self.match(pddlParser.T__0)
                self.state = 611
                self.match(pddlParser.T__27)
                self.state = 612
                self.timeSpecifier()
                self.state = 613
                self.simpleDurationConstraint()
                self.state = 614
                self.match(pddlParser.T__2)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DurOpContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return pddlParser.RULE_durOp

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterDurOp(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitDurOp(self)




    def durOp(self):

        localctx = pddlParser.DurOpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 100, self.RULE_durOp)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 618
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << pddlParser.T__39) | (1 << pddlParser.T__40) | (1 << pddlParser.T__41))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DurValueContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(pddlParser.NUMBER, 0)

        def fExp(self):
            return self.getTypedRuleContext(pddlParser.FExpContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_durValue

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterDurValue(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitDurValue(self)




    def durValue(self):

        localctx = pddlParser.DurValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 102, self.RULE_durValue)
        try:
            self.state = 622
            la_ = self._interp.adaptivePredict(self._input,54,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 620
                self.match(pddlParser.NUMBER)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 621
                self.fExp()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class DaEffectContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def daEffect(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.DaEffectContext)
            else:
                return self.getTypedRuleContext(pddlParser.DaEffectContext,i)


        def timedEffect(self):
            return self.getTypedRuleContext(pddlParser.TimedEffectContext,0)


        def typedVariableList(self):
            return self.getTypedRuleContext(pddlParser.TypedVariableListContext,0)


        def daGD(self):
            return self.getTypedRuleContext(pddlParser.DaGDContext,0)


        def assignOp(self):
            return self.getTypedRuleContext(pddlParser.AssignOpContext,0)


        def fHead(self):
            return self.getTypedRuleContext(pddlParser.FHeadContext,0)


        def fExpDA(self):
            return self.getTypedRuleContext(pddlParser.FExpDAContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_daEffect

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterDaEffect(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitDaEffect(self)




    def daEffect(self):

        localctx = pddlParser.DaEffectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 104, self.RULE_daEffect)
        self._la = 0 # Token type
        try:
            self.state = 654
            la_ = self._interp.adaptivePredict(self._input,56,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 624
                self.match(pddlParser.T__0)
                self.state = 625
                self.match(pddlParser.T__17)
                self.state = 629
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==pddlParser.T__0:
                    self.state = 626
                    self.daEffect()
                    self.state = 631
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 632
                self.match(pddlParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 633
                self.timedEffect()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 634
                self.match(pddlParser.T__0)
                self.state = 635
                self.match(pddlParser.T__22)
                self.state = 636
                self.match(pddlParser.T__0)
                self.state = 637
                self.typedVariableList()
                self.state = 638
                self.match(pddlParser.T__2)
                self.state = 639
                self.daEffect()
                self.state = 640
                self.match(pddlParser.T__2)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 642
                self.match(pddlParser.T__0)
                self.state = 643
                self.match(pddlParser.T__33)
                self.state = 644
                self.daGD()
                self.state = 645
                self.timedEffect()
                self.state = 646
                self.match(pddlParser.T__2)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 648
                self.match(pddlParser.T__0)
                self.state = 649
                self.assignOp()
                self.state = 650
                self.fHead()
                self.state = 651
                self.fExpDA()
                self.state = 652
                self.match(pddlParser.T__2)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class TimedEffectContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def timeSpecifier(self):
            return self.getTypedRuleContext(pddlParser.TimeSpecifierContext,0)


        def daEffect(self):
            return self.getTypedRuleContext(pddlParser.DaEffectContext,0)


        def fAssignDA(self):
            return self.getTypedRuleContext(pddlParser.FAssignDAContext,0)


        def assignOp(self):
            return self.getTypedRuleContext(pddlParser.AssignOpContext,0)


        def fHead(self):
            return self.getTypedRuleContext(pddlParser.FHeadContext,0)


        def fExp(self):
            return self.getTypedRuleContext(pddlParser.FExpContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_timedEffect

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterTimedEffect(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitTimedEffect(self)




    def timedEffect(self):

        localctx = pddlParser.TimedEffectContext(self, self._ctx, self.state)
        self.enterRule(localctx, 106, self.RULE_timedEffect)
        try:
            self.state = 674
            la_ = self._interp.adaptivePredict(self._input,57,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 656
                self.match(pddlParser.T__0)
                self.state = 657
                self.match(pddlParser.T__27)
                self.state = 658
                self.timeSpecifier()
                self.state = 659
                self.daEffect()
                self.state = 660
                self.match(pddlParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 662
                self.match(pddlParser.T__0)
                self.state = 663
                self.match(pddlParser.T__27)
                self.state = 664
                self.timeSpecifier()
                self.state = 665
                self.fAssignDA()
                self.state = 666
                self.match(pddlParser.T__2)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 668
                self.match(pddlParser.T__0)
                self.state = 669
                self.assignOp()
                self.state = 670
                self.fHead()
                self.state = 671
                self.fExp()
                self.state = 672
                self.match(pddlParser.T__2)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FAssignDAContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def assignOp(self):
            return self.getTypedRuleContext(pddlParser.AssignOpContext,0)


        def fHead(self):
            return self.getTypedRuleContext(pddlParser.FHeadContext,0)


        def fExpDA(self):
            return self.getTypedRuleContext(pddlParser.FExpDAContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_fAssignDA

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterFAssignDA(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitFAssignDA(self)




    def fAssignDA(self):

        localctx = pddlParser.FAssignDAContext(self, self._ctx, self.state)
        self.enterRule(localctx, 108, self.RULE_fAssignDA)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 676
            self.match(pddlParser.T__0)
            self.state = 677
            self.assignOp()
            self.state = 678
            self.fHead()
            self.state = 679
            self.fExpDA()
            self.state = 680
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class FExpDAContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def binaryOp(self):
            return self.getTypedRuleContext(pddlParser.BinaryOpContext,0)


        def fExpDA(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.FExpDAContext)
            else:
                return self.getTypedRuleContext(pddlParser.FExpDAContext,i)


        def fExp(self):
            return self.getTypedRuleContext(pddlParser.FExpContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_fExpDA

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterFExpDA(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitFExpDA(self)




    def fExpDA(self):

        localctx = pddlParser.FExpDAContext(self, self._ctx, self.state)
        self.enterRule(localctx, 110, self.RULE_fExpDA)
        try:
            self.state = 695
            la_ = self._interp.adaptivePredict(self._input,59,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 682
                self.match(pddlParser.T__0)
                self.state = 689
                la_ = self._interp.adaptivePredict(self._input,58,self._ctx)
                if la_ == 1:
                    self.state = 683
                    self.binaryOp()
                    self.state = 684
                    self.fExpDA()
                    self.state = 685
                    self.fExpDA()
                    pass

                elif la_ == 2:
                    self.state = 687
                    self.match(pddlParser.T__6)
                    self.state = 688
                    self.fExpDA()
                    pass


                self.state = 691
                self.match(pddlParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 693
                self.match(pddlParser.T__47)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 694
                self.fExp()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ProblemContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def problemDecl(self):
            return self.getTypedRuleContext(pddlParser.ProblemDeclContext,0)


        def problemDomain(self):
            return self.getTypedRuleContext(pddlParser.ProblemDomainContext,0)


        def init(self):
            return self.getTypedRuleContext(pddlParser.InitContext,0)


        def goal(self):
            return self.getTypedRuleContext(pddlParser.GoalContext,0)


        def requireDef(self):
            return self.getTypedRuleContext(pddlParser.RequireDefContext,0)


        def objectDecl(self):
            return self.getTypedRuleContext(pddlParser.ObjectDeclContext,0)


        def probConstraints(self):
            return self.getTypedRuleContext(pddlParser.ProbConstraintsContext,0)


        def metricSpec(self):
            return self.getTypedRuleContext(pddlParser.MetricSpecContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_problem

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterProblem(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitProblem(self)




    def problem(self):

        localctx = pddlParser.ProblemContext(self, self._ctx, self.state)
        self.enterRule(localctx, 112, self.RULE_problem)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 697
            self.match(pddlParser.T__0)
            self.state = 698
            self.match(pddlParser.T__1)
            self.state = 699
            self.problemDecl()
            self.state = 700
            self.problemDomain()
            self.state = 702
            la_ = self._interp.adaptivePredict(self._input,60,self._ctx)
            if la_ == 1:
                self.state = 701
                self.requireDef()


            self.state = 705
            la_ = self._interp.adaptivePredict(self._input,61,self._ctx)
            if la_ == 1:
                self.state = 704
                self.objectDecl()


            self.state = 707
            self.init()
            self.state = 708
            self.goal()
            self.state = 710
            la_ = self._interp.adaptivePredict(self._input,62,self._ctx)
            if la_ == 1:
                self.state = 709
                self.probConstraints()


            self.state = 713
            _la = self._input.LA(1)
            if _la==pddlParser.T__0:
                self.state = 712
                self.metricSpec()


            self.state = 715
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ProblemDeclContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self):
            return self.getToken(pddlParser.NAME, 0)

        def getRuleIndex(self):
            return pddlParser.RULE_problemDecl

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterProblemDecl(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitProblemDecl(self)




    def problemDecl(self):

        localctx = pddlParser.ProblemDeclContext(self, self._ctx, self.state)
        self.enterRule(localctx, 114, self.RULE_problemDecl)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 717
            self.match(pddlParser.T__0)
            self.state = 718
            self.match(pddlParser.T__48)
            self.state = 719
            self.match(pddlParser.NAME)
            self.state = 720
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ProblemDomainContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NAME(self):
            return self.getToken(pddlParser.NAME, 0)

        def getRuleIndex(self):
            return pddlParser.RULE_problemDomain

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterProblemDomain(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitProblemDomain(self)




    def problemDomain(self):

        localctx = pddlParser.ProblemDomainContext(self, self._ctx, self.state)
        self.enterRule(localctx, 116, self.RULE_problemDomain)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 722
            self.match(pddlParser.T__0)
            self.state = 723
            self.match(pddlParser.T__49)
            self.state = 724
            self.match(pddlParser.NAME)
            self.state = 725
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ObjectDeclContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def typedNameList(self):
            return self.getTypedRuleContext(pddlParser.TypedNameListContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_objectDecl

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterObjectDecl(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitObjectDecl(self)




    def objectDecl(self):

        localctx = pddlParser.ObjectDeclContext(self, self._ctx, self.state)
        self.enterRule(localctx, 118, self.RULE_objectDecl)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 727
            self.match(pddlParser.T__0)
            self.state = 728
            self.match(pddlParser.T__50)
            self.state = 729
            self.typedNameList()
            self.state = 730
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class InitContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def initEl(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.InitElContext)
            else:
                return self.getTypedRuleContext(pddlParser.InitElContext,i)


        def getRuleIndex(self):
            return pddlParser.RULE_init

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterInit(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitInit(self)




    def init(self):

        localctx = pddlParser.InitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 120, self.RULE_init)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 732
            self.match(pddlParser.T__0)
            self.state = 733
            self.match(pddlParser.T__51)
            self.state = 737
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pddlParser.T__0:
                self.state = 734
                self.initEl()
                self.state = 739
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 740
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class InitElContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def nameLiteral(self):
            return self.getTypedRuleContext(pddlParser.NameLiteralContext,0)


        def fHead(self):
            return self.getTypedRuleContext(pddlParser.FHeadContext,0)


        def NUMBER(self):
            return self.getToken(pddlParser.NUMBER, 0)

        def getRuleIndex(self):
            return pddlParser.RULE_initEl

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterInitEl(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitInitEl(self)




    def initEl(self):

        localctx = pddlParser.InitElContext(self, self._ctx, self.state)
        self.enterRule(localctx, 122, self.RULE_initEl)
        try:
            self.state = 755
            la_ = self._interp.adaptivePredict(self._input,65,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 742
                self.nameLiteral()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 743
                self.match(pddlParser.T__0)
                self.state = 744
                self.match(pddlParser.T__39)
                self.state = 745
                self.fHead()
                self.state = 746
                self.match(pddlParser.NUMBER)
                self.state = 747
                self.match(pddlParser.T__2)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 749
                self.match(pddlParser.T__0)
                self.state = 750
                self.match(pddlParser.T__27)
                self.state = 751
                self.match(pddlParser.NUMBER)
                self.state = 752
                self.nameLiteral()
                self.state = 753
                self.match(pddlParser.T__2)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class NameLiteralContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def atomicNameFormula(self):
            return self.getTypedRuleContext(pddlParser.AtomicNameFormulaContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_nameLiteral

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterNameLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitNameLiteral(self)




    def nameLiteral(self):

        localctx = pddlParser.NameLiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 124, self.RULE_nameLiteral)
        try:
            self.state = 763
            la_ = self._interp.adaptivePredict(self._input,66,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 757
                self.atomicNameFormula()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 758
                self.match(pddlParser.T__0)
                self.state = 759
                self.match(pddlParser.T__19)
                self.state = 760
                self.atomicNameFormula()
                self.state = 761
                self.match(pddlParser.T__2)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class AtomicNameFormulaContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def predicate(self):
            return self.getTypedRuleContext(pddlParser.PredicateContext,0)


        def NAME(self, i:int=None):
            if i is None:
                return self.getTokens(pddlParser.NAME)
            else:
                return self.getToken(pddlParser.NAME, i)

        def getRuleIndex(self):
            return pddlParser.RULE_atomicNameFormula

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterAtomicNameFormula(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitAtomicNameFormula(self)




    def atomicNameFormula(self):

        localctx = pddlParser.AtomicNameFormulaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 126, self.RULE_atomicNameFormula)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 765
            self.match(pddlParser.T__0)
            self.state = 766
            self.predicate()
            self.state = 770
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==pddlParser.NAME:
                self.state = 767
                self.match(pddlParser.NAME)
                self.state = 772
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 773
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class GoalContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def goalDesc(self):
            return self.getTypedRuleContext(pddlParser.GoalDescContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_goal

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterGoal(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitGoal(self)




    def goal(self):

        localctx = pddlParser.GoalContext(self, self._ctx, self.state)
        self.enterRule(localctx, 128, self.RULE_goal)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 775
            self.match(pddlParser.T__0)
            self.state = 776
            self.match(pddlParser.T__52)
            self.state = 777
            self.goalDesc()
            self.state = 778
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ProbConstraintsContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def prefConGD(self):
            return self.getTypedRuleContext(pddlParser.PrefConGDContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_probConstraints

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterProbConstraints(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitProbConstraints(self)




    def probConstraints(self):

        localctx = pddlParser.ProbConstraintsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 130, self.RULE_probConstraints)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 780
            self.match(pddlParser.T__0)
            self.state = 781
            self.match(pddlParser.T__12)
            self.state = 782
            self.prefConGD()
            self.state = 783
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class PrefConGDContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def prefConGD(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.PrefConGDContext)
            else:
                return self.getTypedRuleContext(pddlParser.PrefConGDContext,i)


        def typedVariableList(self):
            return self.getTypedRuleContext(pddlParser.TypedVariableListContext,0)


        def conGD(self):
            return self.getTypedRuleContext(pddlParser.ConGDContext,0)


        def NAME(self):
            return self.getToken(pddlParser.NAME, 0)

        def getRuleIndex(self):
            return pddlParser.RULE_prefConGD

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterPrefConGD(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitPrefConGD(self)




    def prefConGD(self):

        localctx = pddlParser.PrefConGDContext(self, self._ctx, self.state)
        self.enterRule(localctx, 132, self.RULE_prefConGD)
        self._la = 0 # Token type
        try:
            self.state = 811
            la_ = self._interp.adaptivePredict(self._input,70,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 785
                self.match(pddlParser.T__0)
                self.state = 786
                self.match(pddlParser.T__17)
                self.state = 790
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==pddlParser.T__0:
                    self.state = 787
                    self.prefConGD()
                    self.state = 792
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 793
                self.match(pddlParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 794
                self.match(pddlParser.T__0)
                self.state = 795
                self.match(pddlParser.T__22)
                self.state = 796
                self.match(pddlParser.T__0)
                self.state = 797
                self.typedVariableList()
                self.state = 798
                self.match(pddlParser.T__2)
                self.state = 799
                self.prefConGD()
                self.state = 800
                self.match(pddlParser.T__2)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 802
                self.match(pddlParser.T__0)
                self.state = 803
                self.match(pddlParser.T__26)
                self.state = 805
                _la = self._input.LA(1)
                if _la==pddlParser.NAME:
                    self.state = 804
                    self.match(pddlParser.NAME)


                self.state = 807
                self.conGD()
                self.state = 808
                self.match(pddlParser.T__2)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 810
                self.conGD()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class MetricSpecContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def optimization(self):
            return self.getTypedRuleContext(pddlParser.OptimizationContext,0)


        def metricFExp(self):
            return self.getTypedRuleContext(pddlParser.MetricFExpContext,0)


        def getRuleIndex(self):
            return pddlParser.RULE_metricSpec

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterMetricSpec(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitMetricSpec(self)




    def metricSpec(self):

        localctx = pddlParser.MetricSpecContext(self, self._ctx, self.state)
        self.enterRule(localctx, 134, self.RULE_metricSpec)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 813
            self.match(pddlParser.T__0)
            self.state = 814
            self.match(pddlParser.T__53)
            self.state = 815
            self.optimization()
            self.state = 816
            self.metricFExp()
            self.state = 817
            self.match(pddlParser.T__2)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class OptimizationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return pddlParser.RULE_optimization

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterOptimization(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitOptimization(self)




    def optimization(self):

        localctx = pddlParser.OptimizationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 136, self.RULE_optimization)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 819
            _la = self._input.LA(1)
            if not(_la==pddlParser.T__54 or _la==pddlParser.T__55):
                self._errHandler.recoverInline(self)
            else:
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class MetricFExpContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def binaryOp(self):
            return self.getTypedRuleContext(pddlParser.BinaryOpContext,0)


        def metricFExp(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.MetricFExpContext)
            else:
                return self.getTypedRuleContext(pddlParser.MetricFExpContext,i)


        def NUMBER(self):
            return self.getToken(pddlParser.NUMBER, 0)

        def functionSymbol(self):
            return self.getTypedRuleContext(pddlParser.FunctionSymbolContext,0)


        def NAME(self, i:int=None):
            if i is None:
                return self.getTokens(pddlParser.NAME)
            else:
                return self.getToken(pddlParser.NAME, i)

        def getRuleIndex(self):
            return pddlParser.RULE_metricFExp

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterMetricFExp(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitMetricFExp(self)




    def metricFExp(self):

        localctx = pddlParser.MetricFExpContext(self, self._ctx, self.state)
        self.enterRule(localctx, 138, self.RULE_metricFExp)
        self._la = 0 # Token type
        try:
            self.state = 859
            la_ = self._interp.adaptivePredict(self._input,73,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 821
                self.match(pddlParser.T__0)
                self.state = 822
                self.binaryOp()
                self.state = 823
                self.metricFExp()
                self.state = 824
                self.metricFExp()
                self.state = 825
                self.match(pddlParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 827
                self.match(pddlParser.T__0)
                self.state = 828
                _la = self._input.LA(1)
                if not(_la==pddlParser.T__34 or _la==pddlParser.T__36):
                    self._errHandler.recoverInline(self)
                else:
                    self.consume()
                self.state = 829
                self.metricFExp()
                self.state = 831 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 830
                    self.metricFExp()
                    self.state = 833 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==pddlParser.T__0 or _la==pddlParser.T__56 or _la==pddlParser.NAME or _la==pddlParser.NUMBER):
                        break

                self.state = 835
                self.match(pddlParser.T__2)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 837
                self.match(pddlParser.T__0)
                self.state = 838
                self.match(pddlParser.T__6)
                self.state = 839
                self.metricFExp()
                self.state = 840
                self.match(pddlParser.T__2)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 842
                self.match(pddlParser.NUMBER)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 843
                self.match(pddlParser.T__0)
                self.state = 844
                self.functionSymbol()
                self.state = 848
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==pddlParser.NAME:
                    self.state = 845
                    self.match(pddlParser.NAME)
                    self.state = 850
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 851
                self.match(pddlParser.T__2)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 853
                self.functionSymbol()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 854
                self.match(pddlParser.T__56)
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 855
                self.match(pddlParser.T__0)
                self.state = 856
                self.match(pddlParser.T__57)
                self.state = 857
                self.match(pddlParser.NAME)
                self.state = 858
                self.match(pddlParser.T__2)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

    class ConGDContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def conGD(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.ConGDContext)
            else:
                return self.getTypedRuleContext(pddlParser.ConGDContext,i)


        def typedVariableList(self):
            return self.getTypedRuleContext(pddlParser.TypedVariableListContext,0)


        def goalDesc(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(pddlParser.GoalDescContext)
            else:
                return self.getTypedRuleContext(pddlParser.GoalDescContext,i)


        def NUMBER(self, i:int=None):
            if i is None:
                return self.getTokens(pddlParser.NUMBER)
            else:
                return self.getToken(pddlParser.NUMBER, i)

        def getRuleIndex(self):
            return pddlParser.RULE_conGD

        def enterRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.enterConGD(self)

        def exitRule(self, listener:ParseTreeListener):
            if isinstance( listener, pddlListener ):
                listener.exitConGD(self)




    def conGD(self):

        localctx = pddlParser.ConGDContext(self, self._ctx, self.state)
        self.enterRule(localctx, 140, self.RULE_conGD)
        self._la = 0 # Token type
        try:
            self.state = 937
            la_ = self._interp.adaptivePredict(self._input,75,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 861
                self.match(pddlParser.T__0)
                self.state = 862
                self.match(pddlParser.T__17)
                self.state = 866
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==pddlParser.T__0:
                    self.state = 863
                    self.conGD()
                    self.state = 868
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 869
                self.match(pddlParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 870
                self.match(pddlParser.T__0)
                self.state = 871
                self.match(pddlParser.T__22)
                self.state = 872
                self.match(pddlParser.T__0)
                self.state = 873
                self.typedVariableList()
                self.state = 874
                self.match(pddlParser.T__2)
                self.state = 875
                self.conGD()
                self.state = 876
                self.match(pddlParser.T__2)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 878
                self.match(pddlParser.T__0)
                self.state = 879
                self.match(pddlParser.T__27)
                self.state = 880
                self.match(pddlParser.T__30)
                self.state = 881
                self.goalDesc()
                self.state = 882
                self.match(pddlParser.T__2)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 884
                self.match(pddlParser.T__0)
                self.state = 885
                self.match(pddlParser.T__58)
                self.state = 886
                self.goalDesc()
                self.state = 887
                self.match(pddlParser.T__2)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 889
                self.match(pddlParser.T__0)
                self.state = 890
                self.match(pddlParser.T__59)
                self.state = 891
                self.goalDesc()
                self.state = 892
                self.match(pddlParser.T__2)
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 894
                self.match(pddlParser.T__0)
                self.state = 895
                self.match(pddlParser.T__60)
                self.state = 896
                self.match(pddlParser.NUMBER)
                self.state = 897
                self.goalDesc()
                self.state = 898
                self.match(pddlParser.T__2)
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 900
                self.match(pddlParser.T__0)
                self.state = 901
                self.match(pddlParser.T__61)
                self.state = 902
                self.goalDesc()
                self.state = 903
                self.match(pddlParser.T__2)
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 905
                self.match(pddlParser.T__0)
                self.state = 906
                self.match(pddlParser.T__62)
                self.state = 907
                self.goalDesc()
                self.state = 908
                self.goalDesc()
                self.state = 909
                self.match(pddlParser.T__2)
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 911
                self.match(pddlParser.T__0)
                self.state = 912
                self.match(pddlParser.T__63)
                self.state = 913
                self.goalDesc()
                self.state = 914
                self.goalDesc()
                self.state = 915
                self.match(pddlParser.T__2)
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 917
                self.match(pddlParser.T__0)
                self.state = 918
                self.match(pddlParser.T__64)
                self.state = 919
                self.match(pddlParser.NUMBER)
                self.state = 920
                self.goalDesc()
                self.state = 921
                self.goalDesc()
                self.state = 922
                self.match(pddlParser.T__2)
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 924
                self.match(pddlParser.T__0)
                self.state = 925
                self.match(pddlParser.T__65)
                self.state = 926
                self.match(pddlParser.NUMBER)
                self.state = 927
                self.match(pddlParser.NUMBER)
                self.state = 928
                self.goalDesc()
                self.state = 929
                self.match(pddlParser.T__2)
                pass

            elif la_ == 12:
                self.enterOuterAlt(localctx, 12)
                self.state = 931
                self.match(pddlParser.T__0)
                self.state = 932
                self.match(pddlParser.T__66)
                self.state = 933
                self.match(pddlParser.NUMBER)
                self.state = 934
                self.goalDesc()
                self.state = 935
                self.match(pddlParser.T__2)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx




