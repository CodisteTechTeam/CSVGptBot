import 'dart:convert';

import 'package:flutter/foundation.dart';

import '/flutter_flow/flutter_flow_util.dart';
import 'api_manager.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

export 'api_manager.dart' show ApiCallResponse;

const _kPrivateApiFunctionName = 'ffPrivateApiCall';

class EnvProvider {
  String get APIURLUPLOADenvValue => dotenv.env['BACKENDURL'] ?? 'default_value';

}

class UploadCSVFileCallCall {
  static Future<ApiCallResponse> call({
    FFUploadedFile? file,
  }) async {
    final String apiUrl = EnvProvider().APIURLUPLOADenvValue; 

    return ApiManager.instance.makeApiCall(
      callName: 'UploadCSVFileCall',
      apiUrl: '$apiUrl/upload-file/',
      callType: ApiCallType.POST,
      headers: {},
      params: {
        'file': file,
      },
      bodyType: BodyType.MULTIPART,
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
      isStreamingApi: false,
      alwaysAllowBody: false,
    );
  }
}

class ChatCallCall {
  static Future<ApiCallResponse> call({
    String? queryText = 'give me chart of revenue table',
    String? filename = 'fd1866fd-ce35-4721-953c-be22c6fb207e.csv',
  }) async {
      final String apiUrlQUERY = EnvProvider().APIURLUPLOADenvValue; 
    final ffApiRequestBody = '''
{
  "query_text": "$queryText",
  "filename": "$filename"
}''';
    return ApiManager.instance.makeApiCall(
      callName: 'ChatCall',
      apiUrl: "$apiUrlQUERY/query",
      callType: ApiCallType.POST,
      headers: {},
      params: {},
      body: ffApiRequestBody,
      bodyType: BodyType.JSON,
      returnBody: true,
      encodeBodyUtf8: false,
      decodeUtf8: false,
      cache: false,
      isStreamingApi: false,
      alwaysAllowBody: false,
    );
  }

  static String? query(dynamic response) => castToType<String>(getJsonField(
        response,
        r'''$.query''',
      ));
  static String? answer(dynamic response) => castToType<String>(getJsonField(
        response,
        r'''$.answer''',
      ));
  static String? imageurl(dynamic response) => castToType<String>(getJsonField(
        response,
        r'''$.image_url''',
      ));
}

class ApiPagingParams {
  int nextPageNumber = 0;
  int numItems = 0;
  dynamic lastResponse;

  ApiPagingParams({
    required this.nextPageNumber,
    required this.numItems,
    required this.lastResponse,
  });

  @override
  String toString() =>
      'PagingParams(nextPageNumber: $nextPageNumber, numItems: $numItems, lastResponse: $lastResponse,)';
}

String _toEncodable(dynamic item) {
  return item;
}

String _serializeList(List? list) {
  list ??= <String>[];
  try {
    return json.encode(list, toEncodable: _toEncodable);
  } catch (_) {
    if (kDebugMode) {
      print("List serialization failed. Returning empty list.");
    }
    return '[]';
  }
}

String _serializeJson(dynamic jsonVar, [bool isList = false]) {
  jsonVar ??= (isList ? [] : {});
  try {
    return json.encode(jsonVar, toEncodable: _toEncodable);
  } catch (_) {
    if (kDebugMode) {
      print("Json serialization failed. Returning empty json.");
    }
    return isList ? '[]' : '{}';
  }
}
