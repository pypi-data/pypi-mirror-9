/*
 * This is the structure used to send call info to server.
 */
struct RequestHeader {
    1: string request_id
    2: string seq
}

/**
 * This is the struct that a successful upgrade will reply with.
 */
struct UpgradeReply {}
struct UpgradeArgs {}
