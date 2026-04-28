import 'package:flutter/material.dart';

class VoiceInputButton extends StatelessWidget {
  final bool isListening;
  final VoidCallback onPressed;

  const VoiceInputButton({
    super.key,
    required this.isListening,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: isListening ? Colors.red.shade100 : Colors.blue.shade50,
        shape: BoxShape.circle,
      ),
      child: IconButton(
        icon: Icon(
          isListening ? Icons.mic : Icons.mic_none,
          color: isListening ? Colors.red : Colors.blue.shade700,
        ),
        onPressed: onPressed,
      ),
    );
  }
}
