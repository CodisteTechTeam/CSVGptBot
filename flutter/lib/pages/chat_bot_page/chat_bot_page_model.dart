import '/backend/api_requests/api_calls.dart';
import '/components/chat_view_widget.dart';
import '/flutter_flow/flutter_flow_icon_button.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import '/flutter_flow/flutter_flow_widgets.dart';
import '/flutter_flow/upload_data.dart';
import 'chat_bot_page_widget.dart' show ChatBotPageWidget;
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

class ChatBotPageModel extends FlutterFlowModel<ChatBotPageWidget> {
  ///  Local state fields for this page.

  String? fileName;

  List<dynamic> chatData = [];
  void addToChatData(dynamic item) => chatData.add(item);
  void removeFromChatData(dynamic item) => chatData.remove(item);
  void removeAtIndexFromChatData(int index) => chatData.removeAt(index);
  void insertAtIndexInChatData(int index, dynamic item) =>
      chatData.insert(index, item);
  void updateChatDataAtIndex(int index, Function(dynamic) updateFn) =>
      chatData[index] = updateFn(chatData[index]);

  ///  State fields for stateful widgets in this page.

  final unfocusNode = FocusNode();
  bool isDataUploading = false;
  FFUploadedFile uploadedLocalFile =
      FFUploadedFile(bytes: Uint8List.fromList([]));

  // Stores action output result for [Backend Call - API (UploadCSVFileCall)] action in IconButton widget.
  ApiCallResponse? chatFileUploadResponse;
  // State field(s) for ListView widget.
  ScrollController? listViewController;
  // State field(s) for TextField widget.
  FocusNode? textFieldFocusNode;
  TextEditingController? textController;
  String? Function(BuildContext, String?)? textControllerValidator;
  // Stores action output result for [Backend Call - API (ChatCall)] action in Button widget.
  ApiCallResponse? chatAPIResponse;

  @override
  void initState(BuildContext context) {
    listViewController = ScrollController();
  }

  @override
  void dispose() {
    listViewController?.dispose();
    textFieldFocusNode?.dispose();
    textController?.dispose();
  }
}
